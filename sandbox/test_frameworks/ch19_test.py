import os
import sys
import re

def parse_simple_yaml(yaml_content):
    """Fallback basic parser if PyYAML is not present."""
    data = {}
    for line in yaml_content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        # Check standard key-value pairs
        match = re.match(r"^([\w\-]+)\s*:\s*(.*)$", line)
        if match:
            k, v = match.groups()
            v = v.strip().strip("'\"")
            data[k] = v
    return data

def test_chapter_19():
    print("Testing Chapter 19: Kubernetes Citadel Cluster Layouts...")
    solution_path = "/workspace/ch19_k8s.py"
    if not os.path.exists(solution_path):
        solution_path = "save_data/relic_save/ch19_k8s.py"
        if not os.path.exists(solution_path):
            print("Error: Solution file 'ch19_k8s.py' not found.")
            sys.exit(1)

    import importlib.util
    spec = importlib.util.spec_from_file_location("student_solution", solution_path)
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception as e:
        print(f"Error: Solution script failed to compile: {e}")
        sys.exit(1)

    if not hasattr(module, "get_k8s_manifests"):
        print("Error: Solution must define 'get_k8s_manifests' function.")
        sys.exit(1)

    try:
        pod_yaml, ingress_yaml = module.get_k8s_manifests()
        
        # 1. Validate Pod Manifest
        print("Validating Pod configuration...")
        if "kind: Pod" not in pod_yaml:
            print("Error: Pod manifest is missing 'kind: Pod'")
            sys.exit(1)
            
        if "name: defense-pod" not in pod_yaml:
            print("Error: Pod name must be configured as 'defense-pod'")
            sys.exit(1)
            
        # Check resource allocations
        memory_limit = re.search(r"memory:\s*\"?256Mi\"?", pod_yaml)
        cpu_limit = re.search(r"cpu:\s*\"?500m\"?", pod_yaml)
        memory_req = re.search(r"memory:\s*\"?128Mi\"?", pod_yaml)
        cpu_req = re.search(r"cpu:\s*\"?250m\"?", pod_yaml)
        
        if not (memory_limit and cpu_limit and memory_req and cpu_req):
            print("Error: Pod resource limits/requests are misconfigured or missing. Ensure Limits: 256Mi memory, 500m CPU and Requests: 128Mi memory, 250m CPU.")
            sys.exit(1)
            
        container_port = re.search(r"containerPort:\s*8000", pod_yaml)
        if not container_port:
            print("Error: Pod containerPort must be exposed on 8000.")
            sys.exit(1)
            
        print("Pod Manifest specifications: PASS")

        # 2. Validate Ingress Manifest
        print("Validating Ingress routing...")
        if "kind: Ingress" not in ingress_yaml:
            print("Error: Ingress manifest is missing 'kind: Ingress'")
            sys.exit(1)
            
        if "name: citadel-ingress" not in ingress_yaml:
            print("Error: Ingress name must be 'citadel-ingress'")
            sys.exit(1)
            
        ingress_path = re.search(r"path:\s*/defense", ingress_yaml)
        service_name = re.search(r"name:\s*defense-service", ingress_yaml)
        service_port = re.search(r"number:\s*80", ingress_yaml)
        
        if not (ingress_path and service_name and service_port):
            print("Error: Ingress route rules are incorrect. Ensure path '/defense' links to service 'defense-service' on port 80.")
            sys.exit(1)
            
        print("Ingress Route specifications: PASS")
        
    except Exception as e:
        print(f"Error testing get_k8s_manifests: {e}")
        sys.exit(1)

    print("\n>>> All Chapter 19 tests passed! Kubernetes configs deployed to Citadel scheduler.")
    sys.exit(0)

if __name__ == "__main__":
    test_chapter_19()
