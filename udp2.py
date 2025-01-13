import socket
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit import transpile
from qiskit.visualization import plot_histogram

# Step 1: Define a function to receive measurement results via UDP
def receive_measurements(host='127.0.0.1', port=65432):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
        udp_socket.bind((host, port))
        print("Receiver is waiting for measurement results...")
        while True:
            data, _ = udp_socket.recvfrom(1024)
            print(f"\nReceived Data: {data.decode()}")
            yield map(int, data.decode().split(","))

# Step 2: Set up the simulator
simulator = AerSimulator()

# Step 3: Process incoming measurements in a loop
for m0, m1 in receive_measurements():
    print(f"\nProcessing Measurement Results: m0 = {m0}, m1 = {m1}")
    
    # Create a quantum circuit for the receiver's correction
    qc_receiver = QuantumCircuit(1, 1)  # Receiver uses one qubit (qubit 2)

    # Apply corrections based on the classical information
    if m0 == 1:
        print("Applying X gate to qubit (correction for m0 = 1).")
        qc_receiver.x(0)  # Apply X gate if m0 = 1
    if m1 == 1:
        print("Applying Z gate to qubit (correction for m1 = 1).")
        qc_receiver.z(0)  # Apply Z gate if m1 = 1

    # Measure the final state of the receiver's qubit
    qc_receiver.measure(0, 0)

    # Transpile and simulate the receiver's circuit
    qc_receiver = transpile(qc_receiver, simulator)
    result_receiver = simulator.run(qc_receiver, shots=1024).result()
    counts = result_receiver.get_counts()

    # Display the reconstructed state
    print("\nReconstructed State Results:")
    for state, count in counts.items():
        print(f"  State '{state}' occurred {count} times.")

