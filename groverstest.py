# Import necessary libraries
from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
from qiskit.visualization import plot_histogram
from matplotlib import pyplot as plt
from qiskit_ibm_runtime import Session
from qiskit_ibm_runtime.fake_provider import FakeManilaV2
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager

QiskitRuntimeService.save_account(channel="ibm_quantum", token="f923dfbd31df10a1a6af9e9e62d0043d1087d74b35b6d95dd4fb216d5f154cd869ba935e7be7437e88a5eee7c4dbf16682dc3296d0fe77edd0719b39c7383f6c", overwrite =True)

# Initialize QiskitRuntimeService
service = QiskitRuntimeService()

def grover_oracle(qc, marked_state):
    """Applies an oracle that marks a specific state."""
    for qubit, bit in enumerate(reversed(marked_state)):
        if bit == '0':
            qc.x(qubit)  # Flip qubits corresponding to '0' to ensure marking
    
    qc.h(len(marked_state) - 1)  # Apply Hadamard to the last qubit
    qc.mcx(list(range(len(marked_state) - 1)), len(marked_state) - 1)  # Multi-controlled NOT gate
    qc.h(len(marked_state) - 1)
    
    for qubit, bit in enumerate(reversed(marked_state)):
        if bit == '0':
            qc.x(qubit)  # Revert qubits back to original state

def diffusion_operator(qc, n):
    """Applies the Grover diffusion operator."""
    qc.h(range(n))  # Apply Hadamard to all qubits to create uniform distribution
    qc.x(range(n))  # Apply X gates to flip state around mean
    qc.h(n-1)  # Apply Hadamard to last qubit
    qc.mcx(list(range(n-1)), n-1)  # Multi-controlled NOT gate to amplify correct state
    qc.h(n-1)
    qc.x(range(n))  # Undo the X gates
    qc.h(range(n))  # Final Hadamard transform to complete diffusion

def grovers_algorithm(n, marked_state, iterations=1):
    """Implements Grover's Algorithm for unstructured search."""
    qc = QuantumCircuit(n, n)
    
    # Apply Hadamard gates to all qubits to create superposition
    qc.h(range(n))
    
    # Apply Grover iterations
    for _ in range(iterations):
        grover_oracle(qc, marked_state)  # Apply oracle to mark the desired state
        diffusion_operator(qc, n)  # Apply diffusion to amplify probability of marked state
    
    # Measure all qubits
    qc.measure(range(n), range(n))
    
    return qc

# Define the number of qubits and the marked state
num_qubits = 3  # Example with 3 qubits
marked_state = "101"  # The state to be searched

grover_circuit = grovers_algorithm(num_qubits, marked_state, iterations=1)

# Transpile the circuit for the least busy operational backend
backend = service.least_busy(operational=True, simulator=False)
pm = generate_preset_pass_manager(backend=backend, optimization_level=1)
compiled_circuit = pm.run(grover_circuit)

# Step 5: Wait for the job to complete and retrieve the results
sampler = SamplerV2(backend)
job = sampler.run([compiled_circuit])

print(f"Job ID is {job.job_id()}")

# Wait for the job to complete and get the result
job_result = job.result()
pub_result = job_result[0]

# Get the counts from the result
counts = pub_result.data.c.get_counts()
print(f"Result: {counts}")

# Visualize the result using a histogram
plot_histogram(counts)
plt.hist(counts, bins=30, color='skyblue', edgecolor='black')
grover_circuit.draw('mpl')
plt.show()

