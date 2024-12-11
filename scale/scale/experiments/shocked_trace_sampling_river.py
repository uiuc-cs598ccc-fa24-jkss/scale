import asyncio
from pprint import pprint
from random import randrange
import pandas as pd
import logging
import hashlib
import re
import math

from backends.tempo_client import TempoClient
from river import anomaly
import os
import pathlib


SANITIZE_PATTERNS = [
    re.compile("(GET .*)\\?.*"),
    re.compile("(GET /api/products)/[A-Z0-9]+"),
]

SPANS_CSV_DIR = os.path.join(
    pathlib.Path(__file__).parent.resolve(), "..", "..", "..", "tests", "data", "spans"
)

logging.basicConfig(level=logging.INFO)


def sanitize_operation(operation):
    for pattern in SANITIZE_PATTERNS:
        operation = pattern.sub("\\1", operation)
    return operation


def normalize_duration(duration, max_duration):
    return min(duration, max_duration)

service_encodings = {}
operation_encodings = {}
def featurize(service, operation):
    operation = sanitize_operation(operation)
    service_encoding = service_encodings.get(service)
    if service_encoding is None:
        service_encodings[service] = service_encoding = len(service_encodings)
    operation_encoding = operation_encodings.get(operation)
    if operation_encoding is None:
        operation_encodings[operation] = operation_encoding = len(operation_encodings)
    record = {f"s{service_encoding}": 1, f"o{operation_encoding}": 1}
    return record


# def hash_operation(operation, feature_length):
#     hash_object = hashlib.sha256(sanitize_operation(operation).encode())
#     hash_value = int.from_bytes(hash_object.digest(), "big")
#     features = {str(i): hash_value & (1 << i) for i in range(feature_length)}
#     return features


async def main(
    train_size=10000, # The amount of spans to train on
    shock_test_size=300, # The amount of spans to generate shocks for
    control_size=4000, # The amount of spans to test for anomalies without shocking
    shock_static_bump=5, # A fixed amount of milliseconds to add to a shocked duration
    shock_range=(15, 20), # A range that is used to pick a factor from to multiply a shocked duration by
    feature_length=16, # The number of bits to use from a hashed operation name to perform binary encoding
    max_train_duration=50000, # The maximum duration a span can have to be considered for training
    max_duration=50000, # The maximum duration a span can have when scoring (if higher, it will be capped at this)
    sample_score=0.50, # The minimum score with [0, 1] that will signify a trace as anomalous
    n_trees=12, # Parameter to HST for number of trees to use
    height=7, # Height of each tree. Note that a tree of height `h` is made up of `h + 1` levels and
              # therefore contains `2 ** (h + 1) - 1` nodes.
    window_size=25, # Number of observations to use for calculating the mass at each node in each tree.
    df_source="csv", # Switch between pulling traces from a CSV or from Tempo
    tempo_url="http://localhost:32000", # URL if pulling from Tempo
    csv_path=os.path.join(SPANS_CSV_DIR, "spans_11_7.csv") # Path to CSV if pulling from CSV
    # csv_path=os.path.join(SPANS_CSV_DIR, "spans_tracemesh_style_11_11.csv") # Path to CSV if pulling from CSV
):
    if df_source == "csv":
        spans_df = pd.read_csv(csv_path)
    else:
        client = TempoClient(tempo_url)
        limit = shock_test_size + train_size + control_size
        spans_df = await client.build_span_df(
            84000, limit, query='{trace:rootService != ""}'
        )

    # normal style
    spans_df['duration'] = 1e-6 * (spans_df['end_time_unix_nano'] - spans_df['start_time_unix_nano'])

    # tracemesh style
    # spans_df['duration'] = spans_df['Duration']
    # spans_df['service_name'] = spans_df['OperationName']
    # spans_df['name'] = spans_df['OperationName']
    # spans_df['span_id'] = spans_df['SpanID']
    print(spans_df)

    spans_df = spans_df[spans_df["duration"] < max_train_duration]
    limits = {"dur": (0, max_duration)}

    base = 0
    train_df = spans_df[base:train_size]
    base += train_size
    shock_test_df = spans_df[base : base + shock_test_size]
    base += shock_test_size
    control_df = spans_df[base : base + control_size]

    hst = anomaly.HalfSpaceTrees(
        n_trees=n_trees, height=height, window_size=window_size, seed=42, limits=limits
    )

    # Train model
    for index, span in train_df.iterrows():
        service = span["service_name"]
        operation = span["name"]
        record = featurize(service, operation)
        duration = span["duration"]
        record["dur"] = normalize_duration(duration, max_duration)
        hst.learn_one(record)

    # Record hits for shocked spans
    shock_hits = []
    for index, span in shock_test_df.iterrows():
        shock_factor = randrange(*shock_range)
        service = span["service_name"]
        operation = span["name"]
        record = featurize(service, operation)
        duration = (span["duration"] + shock_static_bump) * shock_factor
        record["dur"] = normalize_duration(duration, max_duration)
        score = hst.score_one(record)
        if score > sample_score:
            shock_hits.append(span["span_id"])

    # Record hits for unshocked spans
    false_positives = []
    for index, span in control_df.iterrows():
        service = span["service_name"]
        operation = span["name"]
        record = featurize(service, operation)
        duration = span["duration"]
        record["dur"] = normalize_duration(duration, max_duration)
        score = hst.score_one(record)
        if score > sample_score:
            false_positives.append(span["span_id"])

    shock_rate = 100 * len(shock_hits) / len(shock_test_df)
    total_rate = 100 * len(false_positives) / len(control_df)
    print(f"Shocked hit on {round(shock_rate, 3)}%")
    print(f"False positives hit on {round(total_rate, 3)}%")


if __name__ == "__main__":
    asyncio.run(main())
