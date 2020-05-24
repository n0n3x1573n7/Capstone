namespace Quantum.QSharpSimpleDES {
    open Microsoft.Quantum.Intrinsic;
    open Microsoft.Quantum.Convert;
    open Microsoft.Quantum.Math;
    open Microsoft.Quantum.Canon;
    open Microsoft.Quantum.Arrays;
    open Microsoft.Quantum.Measurement;
    open Microsoft.Quantum.Diagnostics;
	
	// https://github.com/microsoft/QuantumKatas/blob/master/GroversAlgorithm/ReferenceImplementation.qs
    // non-adjacent version, since S-DES oracle requires measurement
	
    operation OracleConverterImpl_Reference (markingOracle : ((Qubit[], Qubit) => Unit is Adj), register : Qubit[]) : Unit is Adj {
        using (target = Qubit()) {
            within {
                // Put the target into the |-⟩ state
                X(target);
                H(target);
            } apply {
                // Apply the marking oracle; since the target is in the |-⟩ state,
                // flipping the target if the register satisfies the oracle condition will apply a -1 factor to the state
                // (phase kickback trick)
                markingOracle(register, target);
            }
        }
    }
    operation HadamardTransform_Reference (register : Qubit[]) : Unit is Adj {
        
        ApplyToEachA(H, register);

        // ApplyToEach is a library routine that is equivalent to the following code:
        // for (qubit in register) {
        //     H(qubit);
        // }
    }
	
	function OracleConverter_Reference (markingOracle : ((Qubit[], Qubit) => Unit is Adj)) : (Qubit[] => Unit is Adj) {
        return OracleConverterImpl_Reference(markingOracle, _);
    }
	
    operation Oracle_ArbitraryPattern_Reference (queryRegister : Qubit[], target : Qubit, pattern : Bool[]) : Unit is Adj {        
        (ControlledOnBitString(pattern, X))(queryRegister, target);
    }

    operation ConditionalPhaseFlip_Reference (register : Qubit[]) : Unit is Adj {
        // Define a marking oracle which detects an all zero state
        let allZerosOracle = Oracle_ArbitraryPattern_Reference(_, _, new Bool[Length(register)]);
            
        // Convert it into a phase-flip oracle and apply it
        let flipOracle = OracleConverter_Reference(allZerosOracle);
        flipOracle(register);
    }

    operation PhaseFlip_ControlledZ (register : Qubit[]) : Unit is Adj {
        // Alternative solution, described at https://quantumcomputing.stackexchange.com/questions/4268/how-to-construct-the-inversion-about-the-mean-operator/4269#4269
        within {
            ApplyToEachA(X, register);
        } apply {
            Controlled Z(Most(register), Tail(register));
        }
    }
	
    operation GroverIteration_Reference (register : Qubit[], oracle : (Qubit[] => Unit is Adj)) : Unit is Adj {
        oracle(register);
        HadamardTransform_Reference(register);
        ConditionalPhaseFlip_Reference(register);
        HadamardTransform_Reference(register);
    }
	
    operation GroversSearch_Reference (register : Qubit[], oracle : ((Qubit[], Qubit) => Unit is Adj), iterations : Int) : Unit is Adj {
        
        Message($"[*] Grover Iteration : total {iterations} iteration(s).");
        let phaseOracle = OracleConverter_Reference(oracle);
        HadamardTransform_Reference(register);
        
        for (i in 1 .. iterations) {
            
            GroverIteration_Reference(register, phaseOracle);
            //DumpRegister($"enter absolute path here", register);
            Message($"  [+] {i} / {iterations} done");
        }
    }

}