namespace Quantum.QSharpSimpleDES {

    open Microsoft.Quantum.Arrays;
    open Microsoft.Quantum.Bitwise;
    open Microsoft.Quantum.Canon;
    open Microsoft.Quantum.Convert;
    open Microsoft.Quantum.Diagnostics;
    open Microsoft.Quantum.Intrinsic;
    open Microsoft.Quantum.Math;
    open Microsoft.Quantum.Measurement;
    
    /// # Summary
    /// Generates a subkey by left shifting a 10-qubit key.
    ///
    /// # Description
    /// This operation performs [1,2,3,4,5] -> [2,3,4,5,1]
    ///
    /// # Input
    /// ## key
    /// 10-qubit S-DES key array to be left-shifted.
    operation GenerateSubkey(key : Qubit[]) : Unit is Adj {
        PermuteQubits([4,0,1,2,3,9,5,6,7,8], key);
    }

    /// # Summary
    /// Apply S-Box for each candidate input and alter Q if applicable.
    ///
    /// # Description
    /// If the input qubits (EP) has a `input` basis, update output qubits (Q).
    /// For example, if S-Box(0b1011) = 0b01 and EP has basis for 0b1011,
    /// set Q = Q ^ 0b01.
    ///
    /// # Input
    /// ## EP
    /// 4-qubit extended plaintext.
    /// ## Q
    /// 4-qubit array for the total result of S-Box.
    /// ## input
    /// S-Box input basis value.
    /// ## output
    /// S-Box output binary value.
    ///
    operation SBoxApplySingle(EP : Qubit[], Q : Qubit[], input : Int, output : Int) : Unit is Adj {
        using (ancilla = Qubit[3]) {
            let allOneOracle4 = Oracle_ArbitraryPattern_Reference(_, _, [true, true, true, true]);
            within {
                // apply NOT to zero-bits
                // r0 c0 c1 r0
                for(index in 0..3) {
                    if(And(input, 8 >>> index) == 0) {
                        X(EP[index]);
                    }
                }
            }
            apply {
                for(index in 0..1) {
                    if(And(output, (2 >>> index)) != 0) {
                        allOneOracle4(EP, Q[index]);
                    }
                }
            }
        }
    }

    /// # Summary
    /// Apply S-Box type 0 to EP and store result to Q[0..1].
    ///
    /// # Input
    /// ## EP
    /// 4-qubit extended plaintext.
    /// ## Q
    /// 4-qubit for the result of S-Box.
    operation SBox0Apply(EP : Qubit[], Q : Qubit[]) : Unit is Adj {
        let arr = [1, 3, 0, 2, 3, 1, 2, 0, 0, 3, 2, 1, 1, 3, 3, 2];
        for(i in 0..15) {
            if(arr[i] != 0) {
                SBoxApplySingle(EP, Q, i, arr[i]);
            }
        }
    }

    /// # Summary
    /// Apply S-Box type 0 to EP and store result to Q[2..3].
    ///
    /// # Input
    /// ## EP
    /// 4-qubit extended plaintext.
    /// ## Q
    /// 4-qubit for the result of S-Box.
    operation SBox1Apply(EP : Qubit[], Q : Qubit[]) : Unit is Adj {
        let arr = [0, 2, 1, 0, 2, 1, 3, 3, 3, 2, 0, 1, 1, 0, 0, 3];
        for(i in 0..15) {
            if(arr[i] != 0) {
                SBoxApplySingle(EP, Q, i, arr[i]);
            }
        }
    }

    /// # Summary
    /// Apply a single S-DES round with a given intermediate plaintext and subkey.
    ///
    /// # Input
    /// ## P
    /// 8-qubit intermediate plaintext.
    /// ## subkey
    /// 8-qubit subkey for this round.
    operation ApplyRound(P : Qubit[], subkey : Qubit[]) : Unit is Adj {
        // qubits for the result of S-Box
        using (qubits = Qubit[2]) {
            let EP_arr1 = [1,2,3,0];    //[4,1,2,3];
            let EP_arr2 = [3,0,1,2];    //[2,3,4,1];
            let P4      = [3,0,2,1];    //[2,4,3,1];

            // Calculate qubit[0..1]
            within {
                PermuteQubits(EP_arr1, P[4..7]);
                for(index in 0..3) {
                    CNOT(subkey[index], P[index+4]);
                }
                SBox0Apply(P[4..7], qubits);
            }
            apply {
                for(index in 0..1) {
                    CNOT(qubits[index], P[P4[index]]);
                }
            }

            // Calculate qubit[2..3]
            within {
                PermuteQubits(EP_arr2, P[4..7]);
                for(index in 0..3) {
                    CNOT(subkey[index+4], P[index+4]);
                }
                SBox1Apply(P[4..7], qubits);
            }
            apply {
                for(index in 0..1) {
                    CNOT(qubits[index], P[P4[index+2]]);
                }
            }  
        }
    }

    /// # Summary
    /// Apply 2-round S-DES and set target to |1> if the result is identical to cipher.
    ///
    /// # Input
    /// ## plaintext
    /// An 8-bit Int variable storing plaintext.
    /// ## cipher
    /// An 8-bit Int variable storing cipher for this S-DES.
    /// ## key
    /// An 10-qubit key for this S-DES.
    /// ## target
    /// A qubit to indicate the correctness of this S-DES.
    operation PerformSDES(plaintext : Int, cipher : Int, key : Qubit[], target : Qubit) : Unit is Adj {
        let allOneOracle8 = Oracle_ArbitraryPattern_Reference(_, _, [true, true, true, true, true, true, true, true]);
        using(pqubits = Qubit[8]) {
            within {
                // Step 0.      Prepare qubits based on plaintext
                // pqubits : [2^7, 2^6, ..., 2^0]
                for(index in 0..7) {
                    if(And(plaintext, (128 >>> index) ) != 0) {
                        X(pqubits[index]);
                    }
                }
            
                // Step 1-1.    Permute P with IP
                // [1,2,3,4,5,6,7,8] -> [2,6,3,1,4,8,5,7]
                // perm : [3,0,2,4,6,1,7,5]

                PermuteQubits([3,0,2,4,6,1,7,5], pqubits);

                // Step 1-2.    Permute key with P10
                // [1,2,3,4,5,6,7,8,9,10] -> [3,5,2,7,4,10,1,9,8,6]
                // perm : [6,2,0,4,1,9,3,8,7,5]
                PermuteQubits([6,2,0,4,1,9,3,8,7,5], key);

                // Step 2-1.    Generate K1 from key
                GenerateSubkey(key);

                // Step 2-2.    Apply P8
                // [1,2,3,4,5,6,7,8,9,10] -> [1,2,6,3,7,4,8,5,10,9]
                // perm : [0,1,3,5,7,2,4,6,9,8]
                within {
                    PermuteQubits([0,1,3,5,7,2,4,6,9,8], key);
                }
                // Step 2-3.    Apply 1st Round
                apply {
                    ApplyRound(pqubits, key[2..9]);
                }
  
                // Message("Round 1 finished");
            
                // Step 3.      Swap nibbles of P
                PermuteQubits([4,5,6,7,0,1,2,3], pqubits);

                // Step 4-1.    Generate K2 from key
                GenerateSubkey(key);
                GenerateSubkey(key);

                // Step 4-2.    Permute key with P10
                within {
                    PermuteQubits([0,1,3,5,7,2,4,6,9,8], key);
                }
                // Step 4-3.    Apply 1st Round
                apply {
                    ApplyRound(pqubits, key[2..9]);
                }

                // Message("Round 2 finished");

                // Step 5.      Permute P with IP^{-1}
                // [1,2,3,4,5,6,7,8] -> [4,1,3,5,7,2,8,6]
                // perm : [1,5,2,0,3,7,4,6]
                PermuteQubits([1,5,2,0,3,7,4,6], pqubits);
        
            
                // Microsoft BoolArr returns like [2^0, 2^1, ..., 2&6]
                // while our notation is [2^7, 2^6, ..., 2^0]
                //PermuteQubits([7,6,5,4,3,2,1,0], pqubits);
                
                //DumpRegister((), pqubits);
                // !!!!
                for(index in 0..7) {
                    if(And(cipher, 1 <<< (7-index)) == 0) {
                        //Message($"Flip {index}");
                        X(pqubits[index]);
					}
				}
			}
            apply {
                //DumpRegister((), pqubits);
                allOneOracle8(pqubits, target);
			}
        }
    }
    
    /// # Summary
    /// Returns the number of Grover iterations needed to find a single marked
    /// item, given the number of qubits in a register.
    /// 
    /// # Source
    /// https://docs.microsoft.com/en-us/quantum/quickstarts/search
    function NIterations(nQubits : Int) : Int {
        let nItems = 1 <<< nQubits; // 2^numQubits
        // compute number of iterations:
        let angle = ArcSin(1. / Sqrt(IntAsDouble(nItems)));
        let nIterations = Round(0.25 * PI() / angle - 0.5);
        return nIterations;
    }

    operation EncryptSDES(plaintext : Int, cipher : Int, key : Int) : Bool {
        mutable res = false;
        using (qubits = Qubit[11]) {
            for(index in 0..9) {
                if(And(key, 512 >>> index) > 0) {
                    X(qubits[index]);
				}
			}
            PerformSDES(plaintext, cipher, Most(qubits), Tail(qubits));
            set res = IsResultOne(MResetZ(Tail(qubits)));
            ApplyToEach(Reset, qubits);
		}
        return res;
	}

    operation SDESBreakWithGrover(plaintext : Int, cipher : Int) : Unit {
        using (qubits = Qubit[10]) {
            let PerformThisSDES = PerformSDES(plaintext, cipher, _, _);

            GroversSearch_Reference(qubits, PerformThisSDES, NIterations(10));
            
            PermuteQubits([9,8,7,6,5,4,3,2,1,0], qubits);
            let result_key = ResultArrayAsInt(ForEach(MResetZ, qubits));

            Message($"  [+] Result Key          : {result_key}");
            ApplyToEach(Reset, qubits);
		}
        
	}
    @EntryPoint()
    operation HelloQ () : Unit {
        Message("Hello quantum world!");
        // #1 : 0b00010000, 0b00110011, {0b1100010011}
        // #2 : 0b10100101, 0b00110110, {'0011011111', '0010010111'}
        // #4 : 0b11000111, 0b00010100, {0b1001010000, 0b0110010101, 0b0111011101, 0b1000011000}
        let plaintext   = 0b11000111;
        let key         = 0b0111011101;
        let cipher      = 0b00010100;

        Message("S-DES Cryptanalysis with Grover's Algorithm\n");

        Message($"  [+] Plaintext           : {plaintext}");
        Message($"  [+] Original Key        : {key}");
        Message($"  [+] Expected Cipher     : {cipher}");
        Message("\n");
        Message("[*] Checking if cipher match...");
        let doesCipherMatch = EncryptSDES(plaintext, cipher, key);

        if(doesCipherMatch) {
            Message("  [+] Cipher matches with input.");
			SDESBreakWithGrover(plaintext, cipher);
		}
        else {
            Message("  [-] Cipher does not match with input.");
		}
    }
}
