# Import necessary libraries
from qiskit import QuantumCircuit
from qiskit.visualization import plot_histogram
from qiskit.circuit.library import GroverOperator
from qiskit_ibm_runtime import QiskitRuntimeService
from qiskit_ibm_runtime import SamplerV2 as Sampler
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from matplotlib import pyplot as plt
# Initialize QiskitRuntimeService and check available backends
service = QiskitRuntimeService()

# Number of qubits
n = 3

# Create a quantum circuit with 3 qubits and 3 classical bits
qc = QuantumCircuit(n, n)

# Apply Hadamard gates to all qubits (create a superposition state)
qc.h(range(n))

# Define a custom oracle that marks the state |010>
oracle = QuantumCircuit(n)

# Apply X gates to flip qubits if necessary to create the oracle for |010>
oracle.x(0)  # Flip qubit 0
oracle.cz(0, 1)  # Apply a controlled-Z gate to flip the sign of the state |010>

# Apply the oracle to the quantum circuit
qc.append(oracle, range(n))

# Grover diffusion operator (inversion about the mean)
qc.h(range(n))
qc.x(range(n))
qc.h(n-1)
qc.cx(0, 1)
qc.cx(1, 2)
qc.h(n-1)
qc.x(range(n))
qc.h(range(n))

# Measure the qubits
qc.measure(range(n), range(n))

# Visualize the circuit
qc.draw('mpl')

# Step 3: Use the least busy operational backend (excluding simulators)
backend = service.least_busy(operational=True, simulator=False)
pm = generate_preset_pass_manager(backend=backend, optimization_level=1)
isa_circuit = pm.run(qc)
# Step 5: Wait for the job to complete and retrieve the results
sampler = Sampler(backend)
job = sampler.run([isa_circuit])
print(f"Job ID is {job.job_id()}")
# Wait for the job to complete and get the result
job_result = job.result()
pub_result = job_result[0]
# Get the counts from the result
counts = pub_result.data.c.get_counts()
print(f"{counts}")
# Visualize the result
plot_histogram(counts)
plt.hist(counts, bins=30, color='skyblue', edgecolor='black')
plt.show()
