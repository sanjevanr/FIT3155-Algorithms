# FIT3155 Assignment 2 Question 2
# Student Name: Sanjevan Rajasegar 

import sys, random

"""
References:
    This implementation is based on the FIT3155 Lecture Content for week 6: Semi-numerical (or number-theoretic) algorithms

    Additional external references used to support understanding:
        - GeeksforGeeks, Modular Exponentiation (Power in Modular Arithmetic):
            https://www.geeksforgeeks.org/dsa/modular-exponentiation-power-in-modular-arithmetic/
"""

def read_file(file_path: str) -> str:
    """
    This code is responsible for reading an input file and converting it into a single line 
    needed for computation of Boyer Moores which receives inputs: str and pat which are single strings 

    Input: file_path, a string denoting a file path 
    Output: str, a string denoting the file content computed as a single string  
    """  
    f = open(file_path, 'r')
    singleLine = f.read().strip() # removes \t, \n etc.
    f.close()

    return singleLine 

def write_output(matches: list[int], file_path: str) -> str:
    """
    This code is responsible for writing to the output file as specified in the format provided in the 
    FIT3155 specifications

    Input: matches, a list of integers denoting the number of matches based on the pattern matching
    Output: str, a string denoting the file content computed as a single string/character  
    """  
    f = open(file_path, 'w')

    for match in matches:
        f.write(str(match) + '\n')

    f.close()

def modular_exponentiation_by_repeated_squares(base: int, exponent: int, modulo_number: int) -> int:
    """
    Function Description: This function implements the modular exponentiation using the repeated squaring method taught in the FIT3155 Week 6 Lecture Content

    Approach Description: This approach follows the idea of repeatedly squaring the base to compute the required powers of the base, and multiplying the relevant
    powers of the base in order to retrieve the final result. This approach follows the pseudocode provided in the Lecture Content, and is based on the idea of using 
    the binary of the exponent to determine which powers of the base are needed

    Input:
        - base, an integer denoting the base value being exponentiated
        - exponent, an integer denoting the exponent value
        - modulo_number, an integer denoting the modulus value

    Output: result, an integer denoting the result of the modular exponentiation 
    
    Time Complexity Analysis: O(log e) where e is the exponent, as the exponent is repeatedly broken down by an integer dvision of 2

    Space Complexity Analysis: O(1) as as there are no additional data structures used in this function 

    Reference: FIT3155 Week 6 Lecture Content, slide 22
    """
    # initialise result = 1 
    result = 1 

    # successfully compute a^2^i mod n using repeated squaring starting from a^2^0 mod n 

    # this stores the current power needed for the calculation 
    # at the start this is represents base^(2^0) mod modulo, which is base^1 mod modulo
    current_power = base % modulo_number 

    while exponent > 0:
        # if the ith bit of the exponent b is 1 then update result = result * a^2^i mod n 
        # and check if this current power is needed in the final result, aka if the bit is set
        # to 1 in binary (as explained in the lectures)
        if exponent % 2 == 1: 
            result = (result * current_power) % modulo_number

        # successfully compute the next a^2^i mod n value by squaring the current power
        # base^1, base^2, base^4, base^8, base^16, ...
        current_power = (current_power * current_power) % modulo_number

        # move to the next bit through integer division by 2, which is equivalent to right shifting the bits of the exponent
        exponent = exponent // 2

    # final result is the modular exponentiation of a^b mod n
    return result 

def MillerRabin_primality_test(number: int, k_number_of_tests: int) -> bool:
    """
    Function Description: This function implements the Miller Rabin primality test as method taught in the FIT3155 Week 6 Lecture Content, which is used to determine
    if a number n > 3 is a composite or prime number 

    Approach Description: This approach follows the pseudocode provided in the Lecture Content, which segments primality identification into 4 cases based on the properties 
    of running randomised tests of selecting a value a in the range [2, number - 2]. For each chosen a, the function computes xi values and if any of the 4 cases are satisfied, 
    the function can correctly identify the number as composite or prime

    Input:
        - number, an integer denoting the odd number greater than 3 being tested for primality
        - k_number_of_tests, an integer denoting the number of randomised Miller-Rabin tests to conduct

    Output: bool, a boolean where True indicates that number is prime or composite 
    
    Time Complexity Analysis: O(k * log(number)), where k is k_number_of_tests and number is the number being tested for primality as the function conducts k tests and each test conducts 
    modular exponentiation by repeated squares which has logarithmic time complexity 

    Space Complexity Analysis: O(1) as as there are no additional data structures used in this function 

    Reference: FIT3155 Week 6 Lecture Content, slide 35
    
    Assumption: Identify 2 and 3 as primes, and all even numbers as composite, separately
    
    Reference: FIT3155 Week 6 Lecture Content, slide 35
    """
    # filter out assumed numbers immediately (ie. 2 and 3)
    if number == 2 or number == 3:
        return True

    # Factor n-1 as 2ˆs.t, where t is odd 
    s = 0
    t = number - 1

    # while t is even
    while (t % 2 == 0):
        s = s + 1
        t = t // 2 
    # at this stage , n-1 will be 2ˆs.t, where t is odd

    # conduct k FLT tests
    for loop in range(k_number_of_tests):
        # choose random number in [2...n-2]
        a = random.randint(2, number - 2)

        # compute x_0 = x_0 = aˆt mod n
        x0 = modular_exponentiation_by_repeated_squares(a, t, number)

        if x0 == 1: # case 4: slide 34
            continue 
        
        # this stores the previous xi value, which is needed to computer the next xi value 
        xi_minus_1 = x0

        # initialise xs as x0, then update it as xi values are computed
        xs = x0

        # loop (i in [1...s])
        for i in range(1, s + 1):
            # compute xi = (x_{i-1})^2 mod n
            xi = (xi_minus_1 * xi_minus_1) % number

            # xi = aˆ{2ˆi}t mod n = 1
            if xi == 1:
                if xi_minus_1 != number - 1:
                    return False # case 2: slide 34
                else:
                    xs = 1
                    break # case 3: slide 34

            # update xi_minus_1 so the next xi can be computed from the current xi
            xi_minus_1 = xi

            # keep track of the latest xi value for the final xs check
            xs = xi
        
        # 1 mod number = 1 trivially
        if xs != 1: # case 1: slide 34
            return False 

    return True 

def generate_prime_modulus_p(pattern_length: int) -> int:
    """
    Function Description: This function generates a random prime modulus p needed for the pattern matching as described in the assignment specifications 

    Approach Description: As specified in the assignment specifications, the prime modulus p is generated by testing candidates until a prime is found. The 
    candidates are selected by generating random numbers within the specified range of [2^(t-1), (2^t) - 1], where t is max(32, m) and m is the pattern length. 
    The function uses the Miller-Rabin primality test to determine if a candidate is prime, and continues sampling candidates until a prime is found. 
    The number of tests for Miller-Rabin is fixed to 64 as specified in the Lecture Content, which ensures that the probability of incorrectly identifying a composite 
    number as prime is sufficiently low

    Input: attern_length, an integer denoting the length of the pattern 

    Output: randomly_chosen_candidate_prime_modulus, an integer denoting the randomly generated prime modulus 

    Time Complexity Analysis: O(|candidates| * k * log(number)), where |candidates| is the expected number of randomly sampled candidates, k is k_number_of_tests and number 
    is the number being tested for primality. This is because each possible candidate sampled from the random interval calls the function MillerRabin_primality_test()

    Space Complexity Analysis: O(1), as there are no additional data structures used in this function 

    Reference: FIT3155 Week 6 Lecture Content, slide 36
    """
    # t = max(32, m), where m is the pattern length
    t = max(32, pattern_length)

    candidate_lower_bound = 2 ** (t - 1)
    candidate_upper_bound = (2 ** t) - 1

    # based on the Lecture Content,  if k = 64, then the probability of a given odd composite number n to be incorrectly called 
    # a prime is 1 / 2 ^ 128, so we can fix the number of tests to 64 
    k_number_of_tests = 64

    # keep sampling candidate values until a random prime number is found using Miller-Rabin
    while True:
        randomly_chosen_candidate_prime_modulus = random.randint(candidate_lower_bound, candidate_upper_bound)

        # identify all even numbers and skip them as all numbers divisible by 2 are composite
        if randomly_chosen_candidate_prime_modulus % 2 == 0:
            continue # choose another candidate
        
        # test the odd candidate using Miller-Rabin and if this returns true return the chosen candidate the prime modulus 
        if MillerRabin_primality_test(randomly_chosen_candidate_prime_modulus, k_number_of_tests):
            return randomly_chosen_candidate_prime_modulus
        
def k_gram_mapping_helper(input_string: str, randomly_chosen_candidate_prime_modulus: int) -> int:
    """
    Function Description: This function maps a given k-gram into its corresponding semi-numerical value r(S), as required for the pattern matching algorithm in 
    Question 2

    Approach Description: The function treats the input string as a base 128 number, where each character is represented using its ASCII value (as stated in the 
    specifications). Then for each character in the pattern a summation is calculated to represent the r(S) value 

    Input:
        - input_string, a string denoting the k-gram
        - randomly_chosen_candidate_prime_modulus, an integer denoting the randomly generated prime modulus 

    Output: final_rs_value, an integer denoting the computed r(S) value for the pattern

    Time Complexity Analysis: O(m), where m is the length of pattern as each character is processed one by one to produce the summation for the final r(S) value 

    Space Complexity Analysis: O(1), as there are no additional data structures used in this function 
    """
    beta = 128
    final_rs_value = 0

    for character in input_string:
        # new final_rs_value = old final_rs_value * beta + current character
        # representing the summation process as described in the assignment specifications 
        final_rs_value = (final_rs_value * beta + ord(character)) % randomly_chosen_candidate_prime_modulus

    return final_rs_value

def update_window_rs_value_helper(old_rs_value: int, old_character: str, new_character: str, pattern_length: int, randomly_chosen_candidate_prime_modulus: int) -> int:
    """
    Function Description: This function updates the r(S) value of a text window when the window shifts one position to the right during semi-numerical pattern matching

    Approach Description: Without this helper function, the algorithm would need to recompute the r(S) value for every text window from scratch by scanning all characters
    within the pattern length for each window, even when parts of this region are common to the previous r(S) value when scanning through. This would make the matching phase 
    retain a time complexity of O(n * m) where n is the length of the text and m is the length of the pattern. Thus to improve efficiency, this function applies updates on 
    a character by character basis by removing the contribution of the old first character, shifting the remaining characters to accomodate the next character in the text and 
    adding its contribution to the window. This allows the update to occur character by character rather than scanning the entire window repeatedly

    Input:
        - old_rs_value, an integer denoting the r(S) value of the previous text window
        - old_character, a string denoting the character leaving the the old window
        - new_character, a string denoting the character entering the new window
        - pattern_length, an integer denoting the length of the window
        - randomly_chosen_candidate_prime_modulus, an integer denoting the randomly generated prime modulus 

    Output: updated_new_rs_value, an integer denoting the updated r(S) value for the new text window

    Time Complexity Analysis: O(log m), where m is the pattern length, because the function calls the modular exponentiation by repeated squaring helper function to recalculate
    the new exponent 

    Space Complexity Analysis: O(1), as there are no additional data structures used in this function 
    """
    beta = 128

    # remove the contribution of the frontmost character in the old window for the old rs value
    beta_contribution_pattern_length_minus_front_character = modular_exponentiation_by_repeated_squares(beta, pattern_length - 1, randomly_chosen_candidate_prime_modulus)

    # remove the frontmost character from the old window by subtracting its contribution to the old rs value
    new_rs_value = (old_rs_value - ord(old_character) * beta_contribution_pattern_length_minus_front_character) % randomly_chosen_candidate_prime_modulus 

    # shift the remaining characters left and add the new character at the end of the new window 
    updated_new_rs_value = (new_rs_value * beta + ord(new_character)) % randomly_chosen_candidate_prime_modulus

    return updated_new_rs_value 

def semi_numerical_pattern_matching(txt: str, pat: str) -> list[int]:
    """"
    Function Description: This function implements the semi numerical patttern matching algorithm for Question 2 described in the FIT3155 Assignment specifications. It 
    searches for all occurrences of a input pattern in a text by comparing the computer r(S) value of the pattern against the r(S) value of each text window 

    Approach Description: The function begins by generating a random modulus p and computes the required r(S) value of the pattern which will be the basis of comparison 
    within the text. Instead of recomputing the r(S) value of each shifted text window in the text from scratch by iterating through each new character in the text, the function 
    efficiently calculates the first text window once and then calls the update_window_rs_value_helper function to update the r(S) value on a rolling basis. This is done by removing 
    the first character's contribution to the r(S) value, shifting all characters of pattern_length leftward and appending the next character to the text stream for the updated r(S) value 
    contribution. A previous implementation of this function each text window was scanned across the text which would have produced a time complexity of O(n * m) for pattern matching. However, 
    in this case the pattern matching can occur in O(n + m) time. 

    Input:
        - txt, a string denoting the text 
        - pat, a string denoting the pattern

    Output: valid_matches, a list of integers with the 1 based position matches for the output file

    Time Complexity Analysis: O(m + n * log(m)) where n is the length of the text and m is the length of the pattern, as the pattern and first text window are mapped in O(m) time, and then each 
    later window is updated using the update_window_rs_value_helper function, which computes the rolling updated r(S) value in log(m) time by calling the modular_exponentiation_by_repeated_squares
    helper function. Match appending only occurs when the r(S) values match which occurs in constant time 

    Space Complexity Analysis: O(M) where M is the number of valid matches found between the text and pattern as the valid matches found in the pattern matching process are appended to the valid_matches
    array 
    """
    valid_matches = []

    text_length = len(txt)
    pattern_length = len(pat)

    # edge cases (pattern is empty and pattern is longer than text)
    if pattern_length == 0:
        return valid_matches
    if pattern_length > text_length:
        return valid_matches

    # Test random t−bit random candidates for primality until a prime p is found 
    randomly_chosen_candidate_p = generate_prime_modulus_p(pattern_length)

    # Compute r(pat[1 ... m])
    required_rs_value = k_gram_mapping_helper(pat, randomly_chosen_candidate_p) 

    # Compute r(text[1 ... m]) for the first window, this will be updated in the for loop using update_window_rs_value_helper
    current_text_window_rs_value = k_gram_mapping_helper(txt[0 : pattern_length], randomly_chosen_candidate_p)

    # For each j from 1 to n − m + 1:
    for j in range(0, text_length - pattern_length + 1): # n − m + 1 in 0-based indexing 
        if j > 0: # recompute text windows starting after the first character has it's already been calculated from scratch, ensuring the previous r(S) value can be updated rather than recomputed from scratch
            current_text_window_rs_value = update_window_rs_value_helper(current_text_window_rs_value, txt[j - 1], txt[j + pattern_length - 1], pattern_length, randomly_chosen_candidate_p)

        # process the current text window to verify if the r(S) values match 
        current_text_window = txt[j : j + pattern_length]

        if current_text_window_rs_value == required_rs_value:
            if current_text_window == pat: # check if the current text window matches the pattern 
                valid_matches.append(j + 1) # convert to 1-based indexing and append to the matches list 

    return valid_matches

# REFERENCE: Parts of this code snippet was copied from the "Command-line usage tutorial for Assignments"
# document provided in the assignment specifications 
if __name__ == '__main__':

    #retrieve the file paths from the commandline arguments
    _, txt, pat = sys.argv

    txt = read_file(txt)
    pat = read_file(pat)
    matches = semi_numerical_pattern_matching(txt, pat)

    write_output(matches, "output a2q2.txt")
