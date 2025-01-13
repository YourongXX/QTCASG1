import socket
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit import transpile

# Step 1: Create a quantum circuit with 3 qubits and 2 classical bits
qc_sender = QuantumCircuit(3, 2)

# Step 2: Create an entangled Bell pair between qubits 1 and 2
qc_sender.h(1)  # Apply Hadamard gate to qubit 1
qc_sender.cx(1, 2)  # Apply CNOT gate with control qubit 1 and target qubit 2

# Step 3: Prepare the quantum state to be teleported on qubit 0
qc_sender.x(0)  # Example: Apply X gate to initialize qubit 0 in |1⟩ state

# Step 4: Entangle qubit 0 (sender's qubit) with qubit 1
qc_sender.cx(0, 1)  # Apply CNOT gate with control qubit 0 and target qubit 1
qc_sender.h(0)  # Apply Hadamard gate to qubit 0

# Step 5: Measure qubits 0 and 1 and store results in classical bits
qc_sender.measure(0, 0)  # Measure qubit 0 into classical bit 0
qc_sender.measure(1, 1)  # Measure qubit 1 into classical bit 1

# Simulate the sender's circuit using AerSimulator
simulator = AerSimulator()
qc_sender = transpile(qc_sender, simulator)
result_sender = simulator.run(qc_sender, shots=1).result()
measurement = list(result_sender.get_counts().keys())[0]  # Extract measurement results
m0, m1 = int(measurement[1]), int(measurement[0])  # Decode the results

# Step 6: Send measurement results via UDP
def send_measurements(m0, m1, host='127.0.0.1', port=65432):
    message = f"{m0},{m1}"
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
        udp_socket.sendto(message.encode(), (host, port))
    print(f"Sent measurement results: {message}")

send_measurements(m0, m1)
