---
title: "Dynamic Load Scaling via Distributed Trace Sampling & Analysis"
bibliography: cite/references.bib
csl: cite/style.csl
nocite: |
  @*
documentclass: IEEEtran
classoption:
  - conference
author: |
  ```{=latex}
  \author{
  \IEEEauthorblockN{Kevin Mooney, John Durkin, Samson Koshy, Sushil Khadka, Reza Farivar, Jiawei Tyler Gu}
  \vspace{0.2cm} % Adds vertical space between authors and affiliation
  \IEEEauthorblockA{University of Illinois at Urbana-Champaign, Urbana, IL, USA\\
  \texttt{\{}kmoone3, jdurkin3, skosh3, sushil2, farivar2, jiaweig3\texttt{\}}@illinois.edu}
  }
  ```
header-includes:
 - \usepackage{tabularx}
 - \usepackage{float}
 - \usepackage{upgreek}
 - \usepackage{algorithm}
 - \usepackage{algorithmic}
 - \usepackage{graphicx}
 - \usepackage{setspace}
 - \setstretch{1.0}
 - \setlength{\abovedisplayskip}{0pt}
 - \setlength{\belowdisplayskip}{0pt}
 - \setlength{\textfloatsep}{10pt plus 1.0pt minus 2.0pt}
 - \setlength{\floatsep}{10pt plus 1.0pt minus 2.0pt}
 - \setlength{\intextsep}{10pt plus 1.0pt minus 2.0pt}
abstract: |
  Modern systems often use automation for resource scaling. Current automatic scaling systems focus on system-generated metrics like CPU and memory utilization to determine scaling. While these indicators are precise, they often lack insights into the operational performance of applications affected by scaling. Distributed traces model end-to-end requests or transactions as a hierarchical graph of spans, each representing a measured execution point. Trace data can reveal insights into latencies that are not captured by system-level metrics. To address this, we introduce SCALE, an automated resource scaler that uses distributed traces for scaling decisions. SCALE samples trace spans for duration anomalies and processes them through a heuristics-based modeling engine against defined latency thresholds. If thresholds are exceeded, SCALE triggers scaling commands for orchestration systems. SCALE is evaluated using trace data from open-source microservice benchmarks in a Kubernetes cluster.
# PDF output generated with Pandoc
# pandoc -s -C -V links-as-notes=true --pdf-engine=pdflatex -o scale-short-paper.pdf scale-short-paper.md 
---

# I Introduction

Whether running workloads on remote cloud platforms, on-premises clusters, or compute grids, proper resource utilization is one of the most significant factors that can affect operational expenses and capital expenditures. On one end of the spectrum, under-utilizing resources results in wasted costs through unused hardware and network allocation. Conversely, over-utilizing resources can negatively impact response times, causing degradation and failures throughout your application. At a minimum, this can frustrate the client base, while in severe cases, it can lead to detrimental production outages, potentially causing irreparable damage to the company or brand.

Existing technologies for dynamic load scaling are limited.
<!-- While technologies exist to support dynamic load scaling to various degrees, current implementations have their limitations.  -->
@whysolve22 focuses directly on hardware resources such as CPU and memory, 
  where new instances will be created when CPU utilization exceeds a predefined threshold.
Some systems delve deeper, relying on application-generated metrics. 
However, this involves keeping track of the right parts of your application and manually connect the appropriate application metrics to the right scaling actions.

We propose SCALE, a novel technique utilizing distributed tracing data to make 
  scaling decisions based on application performance, 
  as opposed to solely relying on simple metrics. 
SCALE does not depend on a specific decision-making mechanism or 
  orchestration technology;
  instead, 
  it provides abstraction around these two general areas and focuses on differentiating interesting from benign trace data. 
Such a design would allow research to concentrate on anomaly detection within trace data, enabling operators to customize scaling for diverse and heterogeneous architectures. 
SCALE emphasizes on the sampling of distributed tracing for anomalous execution durations. 
In cases where anomalies are detected, 
  the SCALE processor will generate scaling signals based on the analysis of tail latencies of individual calls within those graphs.

# II Background & Characterization

## A. Related Works

In our research, we drew particular motivation from gaps in the current state of the art of autoscaling systems pointed out
by our fellow researchers.  Much of this fell in line with our vision, and helped reinforce the direction we took in our
own implementation.

### 1) Autoscaling

Straesser et al. @whysolve22 argue that state-of-the-art autoscalers are often too complex for production and rely heavily on CPU metrics. However, performance for some applications is not driven by CPU or memory, making a combination of platform and application metrics beneficial. However, there is also a lack of general-purpose autoscalers for these needs.

Eder et al. @comdist23 emphasize the importance of considering deployment costs in pay-per-use models and ensuring distributed tracing does not degrade application performance. They found that the performance impact—measured in runtime, memory usage, and initialization—varies with tools like Zipkin @zipkin24, Otel @otel24, and SkyWalking @skywalking24. They conclude that with proper tool selection, the benefits of distributed tracing can outweigh performance downsides.

Yu et al. @microscaler19 proposed MicroScaler, which identifies services needing scaling to meet SLA requirements by collecting service metrics (QoS, latency) through proxy sidecars in microservice architectures. While novel, it bases scaling solely on latency and introduces sidecar overheads.

### 2) Sampling

Modern distributed applications are complex, needing deep insights into request orchestration across services. Distributed tracing provides this view but can generate terabytes of trace data daily, complicating processing and storage. Sampling helps maintain efficiency while managing data overload.

The common strategy used by tools like Jaeger @jaeger24 and Zipkin @zipkin24 is uniform random sampling, or head-based sampling, where decisions are made at a trace's start. This method often captures redundant traces, limiting anomaly detection value.

To improve this, tail-based sampling defers decisions until a trace is complete, focusing on traces likely to be informative or anomalous. It is widely adopted in academia and industry. For instance, Tracemesh @tracemesh24 uses DenStream @denstream06 for clustering streaming data, sampling traces
based on their evolving characteristics to cut back on oversampling. Sieve @sieve21 applies a biased sampling method using attention scores with Robust Random Cut Forests (RRCF) to identify uncommon traces. Both leverage trace structural and temporal variations to boost sampling effectiveness. Sifter @sifter19 prioritizes diverse traces by weighting sampling decisions towards those that are underrepresented in its model, thus improving trace variety. Las-Casas et al. @weighted18 proposed a weighted sampling method using a hierarchical clustering technique called Purity Enhancing Rotations for Cluster Hierarchies (PERCH) to ensure diversity in selected traces.

## B. Human Insight vs. Machine Learning

When surveying the landscape of current autoscaling systems, one significant choice that arises is whether to take a heuristics-based approach or to use a fully automated approach. Many original scaling systems were based on heuristics. It is, of course, easier to implement a simple rules-based parser than to design a fully automated system. This allows you to leverage common domain knowledge and directly apply scaling semantics that you believe best serve the health of your system. However, this approach has some obvious drawbacks. The most notable issue is the constant need for human intervention. You will undoubtedly spend well-focused man-hours devising your scaling rule set, and then whatever time it takes to put pen to paper. This is also not a one-time cost. As your system evolves due to planned architecture changes or unforeseen circumstances, you will continuously need to rework your scaling model. Beyond the manual overhead that this approach entails, there’s the fact that humans are not infallible; any scheme they devise, while hopefully sound, is unlikely to be fully optimal.

# III Design

## A. Overview

We introduce SCALE, a software system which analyzes various system and application generated
observability data in order to perform dynamic scaling of application work loads in cloud hosted and/or on-premises environments.
We envision a monitor that can make use of open technologies to probe distributed tracing and metric data.  This system would wire up to client APIs of a diverse set of process orchestration software. This can include container orchestrators, serverless function controllers or VM provisioning frameworks amongst others.  Based on processing of the observability data, a processor will make
vertical or horizontal scaling decisions.  These decisions will then be communicated to the orchestration systems via their 
client API to carry out the scaling action.

While we aim for extensibility, the true novelty of our research hinges on the viability of making scaling decisions 
based on distributed tracing data.  Hence, our implementation will directly focus on the consumption, sampling and analysis of traces.
The analysis centers around a heuristics based trace processor which will check trace spans for latency breaches above configured
thresholds.  Based on actions attached to those thresholds, when breached, the processor will initiate scaling directives via a shim
that sits atop of the Kubernetes API.

```{=latex}
\begin{figure}[t]
  \includegraphics[width=\linewidth]{img/scale-architecture-3.png}
  \caption{SCALE Architecture}
  \label{scale_arch}
\end{figure}
```
Figure \ref{scale_arch} represents the core architecture of SCALE.  The three major components which make up SCALE itself are the *sampler*, *processor*, and *orchestration shim*.  These components work together to form a cohesive, modular workload scaler.  
SCALE is dependent upon a distributed trace storage mechanism and a distributed trace delivery mechanism which leverage OpenTelemetry @otel24. In our implementation we use Grafana Tempo @tempo24 and OpenTelemetry Collector respectively. 

## B. Sampler

The sampler is the first direct SCALE component within the architecture's overall pipeline.  The job of the sampler is to sample trace spans for anomalies before they are sent downstream for scaling determination.  This allows SCALE to predetermine interesting traces in a fast manner, so that extra resources are not wasted on a deep analysis of the call graph.  Downstream the SCALE processor relies on a heuristics based examination of traces.  However, there is a non-insignificant overhead involved in analyzing large call graphs that should be avoided if possible.  This would be further exacerbated if the processor (described in Section III-B4) were swapped for an implementation that relied on a more compute intensive approach. 

At it's core the main purpose of the sampler is to identify trace spans that have unusual durations.  Many of the researched works attempt to perform a holistic sampling of distributed traces.  This is often to identify anomalies in both newly seen call graphs in addition to call durations.  In our case we are only interested in anomalies in the duration of calls.  Given this our sampling is performed directly on each span individually.  This leads to both a more deterministic and more performant implementation.

Spans in open telemetry contain four distinct attributes that are important to our sampling.  The first of these two are the service name and operation name.  The service name is taken to mean a collection of instances of a specific service as opposed to a single running instance.  The operation name denotes a specific unit of execution within a service.  Together these help us to uniquely identify very specific call points within a distributed system for classification.  The second of the two attributes are start and end time in nanoseconds since Unix epoch.  Each span _S_ is thus characterized by:
```{=latex}
\vspace{-1em}
\begin{itemize}
    \item \textbf{Service name:} \( s \)
    \item \textbf{Operation name:} \( o \)
    \item \textbf{Start time:} \( t_{\text{start}} \)
    \item \textbf{End time:} \( t_{\text{end}} \)
\end{itemize}
\vspace{-1em}
The \textbf{Duration} \( D \) of a span is computed as:
\begin{equation}
D = t_{\text{end}} - t_{\text{start}}
\end{equation}
```

The sampler uses Half-Space-Trees (HS-Tree) @hst11 to perform anomaly detection on the durations of spans.  An online variant of isolation forests, HS-Tree provides a model for fast one-class anomaly detection within evolving data streams.  With HS-Tree you provide bounds on the data space which features can fall within.  Multiple trees are then formed based on whether features fall within one half of the bound or the other, with different trees holding different orderings of features.  All trees are sampled, and a prediction is formed from a consensus of the results from all trees.  HS-Tree is best suited for cases where anomalies are rare which is the expectation in distributed trace data.  The HS-Tree model isolates anomalies based on isolation depth _h_, producing an anomaly score:

```{=latex}
\vspace{-1em}
{
  % Locally ensure no extra space before/after displays
  \setlength{\abovedisplayskip}{0pt}
  \setlength{\belowdisplayskip}{0pt}
  \begin{equation}
    \text{Anomaly Score} = 2^{\frac{-h}{H}}
  \end{equation}\vspace{-1em} % reduce space after the equation
  where:\[
    \text{H} = \text{maximum tree height}
  \]\vspace{-2em} % reduce space after the display math
}
```

A number of proven open source implementations exist, and for SCALE we chose to go with from River @river24 an online machine learning library for Python.

To categorize the service and operation name we use one-hot encoding.  The river HS-Tree implementation is able to accept a sparse python dictionary that does not contain
the entire feature set of your data space.  Given this, we simply use simple numerically increasing integers as keys for the feature name of the service and operation.
```{=latex}
Each span is represented by the following feature set (where \textit{OneHotEncode} is defined in \textbf{Algorithm \ref {alg:one_hot_encode}}):
\begin{equation}
\mathbf{X} = \{ \text{OneHotEncode}(s, o), D \}
\end{equation}
\vspace*{-.5em}
\begin{algorithm}
\caption{One-Hot Encoding Function}
\label{alg:one_hot_encode}
\begin{algorithmic}[1]
    \STATE Initialize an empty dictionary \texttt{encodings}
    \STATE \textbf{Function} \texttt{OneHotEncode}(service, operation)
    \STATE $call\_name \gets service + "::" + operation$
    \STATE $encoding \gets encodings.\texttt{get}(call\_name)$
    \IF{$encoding$ is \texttt{None}}
        \STATE $encoding \gets \texttt{len}(encodings)$
        \STATE $encodings[service] \gets encoding$
    \ENDIF
    \STATE $record \gets \{ \texttt{str}(encoding) : 1 \}$
    \RETURN $record$
    \STATE \textbf{End Function}
\end{algorithmic}
\end{algorithm}\vspace{-2em}
```
We then take the difference of the end timestamp minus start timestamp and scale these to milliseconds.  This is added as a second feature to the record and passed into the River HS-Tree model for sampling.  To initially train the HS-Tree model, a pre-configured set of traces are queried from Tempo via an HTTP REST service which provides traces in OpenTelemetry protocol buffer format.  The traces are stored in a pandas data frame as they are collected.  When all traces have been pulled, the model is trained which each span featurized as per the above described algorithm.  The sampler has six core parameters which are used to calibrate the model prior to training:
```{=latex}
\vspace{-1em}
\begin{table}[H]
  \caption{Sampler Parameters}
  \begin{tabularx}{\columnwidth}{l|p{5.5cm}}
    \hline
    Parameter                 & Description \\
    \hline
    n\_tree                   & number of HS-Trees \\
    height                    & height of each HS-Tree \\
    window\_size              & observations in each HS-Tree node \\
    min\_score                & minimum score required for sampling \\
    max\_duration             & maximum bound for duration feature \\
    train\_size               & number of spans to train the model\\
    \hline
  \end{tabularx}
  \label{table: sampler_parameters}
\end{table}
\vspace{-1em}
```
After the model has been successfully trained according to the parameters, the sampler starts a gRPC listener which exposes two RPCs.  The first is an implementation of the OTLP gRPC interface for receiving traces.  As shown in figure \ref{scale_arch}, this allows Collector to stream new traces into the sampler as they are received from upstream applications and infrastructure.  The second RPC provides a streaming endpoint which clients can connect to in order to receive sampled spans, which are provided to the client in their entirety as they were received from Collector.  These together along with the core sampler logic essentially form a streaming pipeline of spans, with the OTLP endpoint as the source, the sampler logic as a filter and the client endpoint as a sink.

## C. Processor

As described, the processor serves as a downstream component of the sampler within the SCALE architecture.  It is the task of the processor to analyze traces and make the ultimate decision on whether to perform any scaling operations.  The processor is configured with a set of rules defined via YAML configuration.  These rules associate latency thresholds with scaling actions.  An example of this is of the form _scale service A if operation B reaches a latency of X, N times within a given window._  The rules then drive the heuristics based analysis of the distributed traces received from the sampler.  

```{=latex}
Scaling actions are triggered when specific thresholds are exceeded:
\begin{equation}
\text{Action} \iff \text{Count}(D > T, \text{window}) \geq N
\end{equation}
The system distinguishes between load bottlenecks and resource constraints, applying appropriate scaling decisions:
\begin{equation}
\text{Scale}(s, o) = 
\begin{cases} 
\text{Horizontal}, & \text{if load bottleneck} \\ 
\text{Vertical}, & \text{if resource bound} 
\end{cases}
\end{equation}
```

The processor is composed of two main components, the consumer and processor engine.  The consumer will initiate a streaming gRPC connection to receive the sampled spans using the Python asyncio version of gRPC.  The spans received contain all of the same attributes and metadata that were also received by the sampler.  These spans are somewhat hierarchical, but not organized according to traces, and more so to shared data between spans for compaction purposes.  The spans are then dropped into an asyncio queue.  

The processor engine will then read these spans from the queue.  The spans are iterated over and flattened into a pandas dataframe.  The rule set defined in the configuration file is then applied as precompiled predicates against the dataframe.  Any rules whose criteria is a match has their actions folded into a conflated action set.  The purpose of conflation is to deduplicate redundant scaling actions.  When the analysis is complete the processor will then call the Kubernetes shim to perform the scaling action.  In addition to scaling analysis and actions, the processor engine will also continually keep several statistics and trend analytics of inspected spans.

## D. Orchestration Shim

The orchestration shim acts as a layer between the processor and Kubernetes itself.  Its purpose is to abstract away the specific details of the Kubernetes API, in order to provide a more generic scaling interface to the processor.  This abstraction model allows for the ability to swap out service orchestration backends, or more realistically to compose multiple backends.  This is manifested in the form of an OrchestrationClient interface which provides a stub for scaling a resource, and another for getting the current scale of a resource.  The shim is meant to be intentionally light weight, and implementations are called directly within the processor.

```{=latex}
\begin{figure}[t]
  \includegraphics[width=\linewidth]{img/scale-flow.png}
  \caption{SCALE Workflow}
  \label{scale_flow}
\end{figure}
```

# IV Evaluation

To evaluate our system, we will create a comprehensive testing environment that simulates 
real-world traffic patterns, bottlenecks, and resource constraints. This setup will allow for
controlled comparisons between baseline autoscaling (CPU/memory-based) and SCALE. We will evaluate the autoscaling systems using open-source
benchmarking suites, along with an in-house architecture resembling a personal finance application. To simulate production-like
environments, we will use additional open-source simulation tools and chaos testing tools to
generate realistic traffic surges and failure conditions across microservices. Our goal is to
measure the speed and accuracy of autoscaling decisions made by the observability-driven
system compared to the baseline.

## A. Parameter Tuning 
The performance of the proposed sampling mechanism was optimized by tuning critical parameters to achieve a balance across four key metrics:

### 1) False Positive Rate (FPR)
FPR measures the proportion of normal spans that are incorrectly flagged as anomalous.  This metric is critical for reducing noise in the system.
```{=latex}
\vspace{-1em}
\setlength{\abovedisplayskip}{0pt}
\setlength{\belowdisplayskip}{0pt}
\begin{equation}
\text{FPR} = \frac{\text{False Positives (FP)}}{\text{Total Normal Spans}}
\end{equation}
```
### 2) Accuracy 
Accuracy quantifies the proportion of correctly classified spans, encompassing both true positives (TP) and true negatives (TN), relative to the total number of spans.  Ensuring 100% accuracy was prioritized to avoid misclassification of both normal and anomalous spans.
```{=latex}
{
  \vspace{-1em}
  \setlength{\abovedisplayskip}{0pt}%
  \setlength{\belowdisplayskip}{0pt}%
  \begin{equation}
    \text{Accuracy} = \frac{\text{True Positives (TP)} + \text{True Negatives (TN)}}{\text{Total Spans}}
  \end{equation}%
  \vspace{-1em}%
}
```
### 3) Processing Time Per Span
This metric reflects the computational efficiency of the sampler by averaging the time required to process each span. Reducing the value is critical to ensure scalability in high-throughput environments.
```{=latex}
{
  \vspace{-1em}
  \setlength{\abovedisplayskip}{0pt}%
  \setlength{\belowdisplayskip}{0pt}%
  \begin{equation}
    T_{span} = \frac{T_{total}}{TotalSpans}
  \end{equation}%
  \vspace{-1em}%
}
```
### 4) F1 Score
The F1 Score provides a balanced measure of the sampler’s precision and recall, capturing the trade-off between correctly identifying anomalies and minimizing false positives. 
```{=latex}
{
  \vspace{-1em}
  % Locally ensure no extra space before/after displays
  \setlength{\abovedisplayskip}{0pt}
  \setlength{\belowdisplayskip}{0pt}
  
  \begin{equation}
    \text{F1} = 2 \cdot \frac{\text{Precision} \cdot \text{Recall}}{\text{Precision} + \text{Recall}}
  \end{equation}\vspace{-1em} % reduce space after the equation
  where:
  \[
    \text{Precision} = \frac{\text{TP}}{\text{TP} + \text{FP}}, \quad \text{Recall} = \frac{\text{TP}}{\text{TP} + \text{FN}}
  \]\vspace{-1em} % reduce space after the display math
}
```
The tuning process involved systematic adjustments of parameters such as the target anomaly score, feature scaling factors, height, number of trees, and window size.  Each iteration was evaluated against the aforementioned metrics with the goal of minimizing FPR, maintaining 100% detection accuracy, reducing processing time, and maximizing the F1 score.  These adjustments were guided by a feedback loop, enabling continuous improvement to optimize sampler performance. 

## B. Dataset Analysis

The optimized sampler was evaluated against two datasets used in previous studies _(GTrace @gtrace23 and TraceMesh @tracemesh24)_.  For both datasets, the sampler was benchmarked on the following metrics: precision, recall, F1 score, processing time, and FPR.  Results demonstrated the sampler consistently maintained 100% accuracy, minimized FPR, and delivered competitive F1 scores while adhering to stringent efficiency requirements.   Table \ref{dataset_comparison} shows the results of these experiments, while \ref{cm_tracemesh} presents a confusion matrix visualizing accuracy against expected results.
```{=latex}
{
  % Reduce spacing for captions and floats
  
  \begin{table}[H]
    \caption{Dataset Comparison}%
    \begin{tabularx}{\columnwidth}{l|X|X}
      \hline
      Metric & GTrace & TraceMesh \\
      \hline
      Total Spans & 4881687 & 57908 \\
      Anomalies Detected & 196987 & 4344 \\
      True Positives & 81361 & 2895 \\
      False Positives & 115626 & 1449 \\
      False Negatives & 0 & 0 \\
      Precision & 0.41302726 & 0.66643646 \\
      Recall & 1.0 & 1.0 \\
      F1 Score & 0.58459913 & 0.79983423 \\
      Processing Time & 71$\upmu$s & 77$\upmu$s \\
      \hline
    \end{tabularx}
    \label{dataset_comparison}
  \end{table}
}
```

```{=latex}
  \begin{figure}[h]
    \setlength{\abovedisplayskip}{0pt}%
    \setlength{\belowdisplayskip}{0pt}%
    \includegraphics[width=\linewidth]{img/cm_tracemesh.png}%
    \caption{TraceMesh Dataset Confusion Matrix}%
    \label{cm_tracemesh}%
  \end{figure}%
```
# V Conclusion
In this paper we put forward the argument for a system capable of performing resource autoscaling decisions based upon distributed trace data as opposed to system level metrics, common in state of the art. To further this proposal, we implemented the SCALE framework.  Rather than examine every trace that is generated by a distributed system, SCALE samples individual trace spans for anomalistic durations.  Sampling is provided via half-space trees, a fast online anomaly detection model for evolving data streams.  Sampled spans are then passed through a heuristics based processor that checks spans against a set of thresholds, and performs scaling actions if defined thresholds are breached.  Through experimentation, we demonstrated performance and accuracy benefits of using half-space trees for span anomaly detection, as well as the benefit of utilizing sampled traces in general.

\pagebreak

# References

