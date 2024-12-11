import os
import subprocess

proto_path = "../proto"
scale_proto_path = "../proto/sampler"  # The source directory for proto files
output_path = "../scale/generated"  # The target directory for generated files

# Find all .proto files recursively
proto_files = []
for root, dirs, files in os.walk(scale_proto_path):
    for file in files:
        if file.endswith(".proto"):
            proto_files.append(os.path.join(root, file))

# Ensure the output directory exists
os.makedirs(output_path, exist_ok=True)

# Compile each .proto file
for proto_file in proto_files:
    command = [
        "python",
        "-m",
        "grpc.tools.protoc",
        f"--proto_path={proto_path}",
        f"--python_out={output_path}",
        f"--pyi_out={output_path}",
        f"--grpc_python_out={output_path}",
        proto_file,
    ]
    subprocess.run(command, check=True)

for root, dirs, files in os.walk(output_path):
    for directory in dirs:
        with open(os.path.join(root, directory, "__init__.py"), "a"):
            pass