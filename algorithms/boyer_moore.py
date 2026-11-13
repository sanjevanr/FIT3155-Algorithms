import sys

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

def write_runlog(runlog: list[str], file_path: str) -> str:
    """
    This code is responsible for writing to the runlog file as specified in the format provided in the 
    FIT3155 specifications

    Input: runlog, a list of strings where each string is formatted as: "<j> <k+1> <p>" representing the 
    current iteration's alignment index, mismatch position and shift value p 
    Output: str, a string denoting the file content computed as a single string  
    """  
    
    f = open(file_path, 'w')

    for line in runlog:
        f.write(line + '\n')

    f.close()

def ZAlgorithm(string: str) -> list[int]:
    """
    Function Description: This code implements Gusfields Z-Algorithm as taught in the Week 1 lecture 
    in FIT3155, which takes a string and computes a Z Array containing the length of the longest substring(s) 
    which match the prefix of the corresponding string.

    Approach Description: As the pattern matching described in the problem relies on an efficient way of comparing 
    substrings to prefixes without repeatedly rescanning naively, I chose to implement the Z Algorithm as it computes
    the Z array in linear time 

    Input: str, a string for which the Z Array is computed 

    Output: list[int], a list of integers in which each index stores the length of the longest possible substring 
    matching the prefix of the input 

    Time Complexity Analysis: O(n) where n is the length of the string. Each character is processed at most a constant 
    number of times by using the Z-Box boundaries 

    Space Complexity Analysis: O(n), where n is the length of the string. This is needed for the outputting of the 
    corresponding Z Array

    REFERENCE: GeeksforGeeks' article "Z algorithm in Python" was used to help understand the case-based logic of the 
    Z-Algorithm: https://www.geeksforgeeks.org/dsa/z-algorithm-in-python/
    """
    # compute the initial empty z array, l and r values (which will be updated)
    n = len(string)
    zArray = [0] * n
    l = 0
    r = 0

    for k in range(1, n): # 0 based indexing so we're going from [2...N] as described in the logic of the lectures
        # Case 1: Explicit comparisons against the prefix are needed
        if k > r:
            
            # create a new Z-Box
            r = k
            l = k
            
            # while the value of r < n AND the substring matches the prefix of the string
            # keep extending r
            while (r < n) and (string[r - l] == string[r]):
                r += 1

            zArray[k] = r - l # story the length of the matched substring 
            r -= 1 # move r back to the last index which was STILL a match 

        # Case 2: We are already inside a Z-Box, and must use pre-defined values from the Z Array
        else:
            mirrorPos = k - l # in the lectures this is k - l + 1 but we're using 0 based indexing 

            # Case 2a: Zk < r - k + 1 (to denote inclusivity differing from 0 based logic as described above)
            if zArray[mirrorPos] < r - k + 1: 
                zArray[k] = zArray[mirrorPos]
            
            # Case 2b: Zk >= r - k + 1 (to denote inclusivity differing from 0 based logic as described above)
            # explicit comparisons may be needed beyond the boundary of r - k + 1
            else: 
                # create a new Z-Box
                l = k 
                r += 1 # start outside the Z-Box to explicitly match 
                
                # while the value of r < n AND the substring matches the prefix of the string
                # keep extending r
                while r < n and string[r] == string[r - l]: 
                    r += 1 

                zArray[k] = r - l
                r -= 1 # last value before a mismatch occurred 

    return zArray  

def modified_good_suffix_rule_array(pat: str) -> list[int]:
    """
    Function Description: This function processes the possible shift positions for p using the good suffix logic 
    used in normal Boyer Moore's all while doing it in a modified way. This is ensured in which for each possible 
    mismatch posiiton the function stores the LEFTMOST shift index possible 

    Approach Description: 
    As the assignment specifies the following conditions:
        1. pat[k + 1 .. k + m − p + 1] = pat[p .. m]: The suffix of the pattern much re-appear at an earlier region 
           from k + 1
        2. The minimum possible shift must ensure: p > k + 1 -> k < p - 1 = k = p - 2 (at maximum)

    As a non-zero value in the Z Suffix array indicates that there is some substring ending at an index which matches a
    suffix of the pattern, this can be used to determine the shifts possible. We use this to then modify the logic further
    by ensuring the LEFTMOST possible position is achieved which can then be used to verify condition 1 needed for the 
    pattern matching approach 

    Input: pat, a string denoting the desired patter

    Output: good_suffix_array, a list of integers denoting the smallest 1 based index p for the position k. This keeps all
    required values based on 1-based indexing as explained in the lecture content/notes

    Time Complexity Analysis: O(m), where m is the length of the pattern as the pattern is reversed once,
    Z Algorithm is applied, and two linear searches are achieved

    Space Complexity Analysis: O(m), where m is the length of the pattern as we store the z_suffix_array and good suffix array
    """
    size = len(pat)

    # reverse the pattern and run Z-Algorithm to extract the Z-Sufix array as shown in the lectures
    reversed_pattern = pat[::-1]
    Zsuffix_array_reversed = ZAlgorithm(reversed_pattern)
    Zsuffix_array = Zsuffix_array_reversed[::-1]

    good_suffix_array = [0] * (size + 1) # create the good suffix of size + 1 as shown in the lectures

    for k_plus_1 in range(size - 1): # ignore the last character to follow the same consistency from the lectures
        if Zsuffix_array[k_plus_1] > 0: # given a suffix match exists use this to now determine p, k
            
            p_value = k_plus_1 + 1 # 1-based index from which shift values can be determined (this satisfies the condition p > k + 1 or equivalently p = k + 2)
            k_value = k_plus_1 - 1 # 1-based index denoting the point of mismatch 

            # as we're assuming 1-based indexing k >= 1 for a mismatch position to be recognised
            # this condition would fail when k_plus_1 = 0 (k = -1) and when k_plus_1 = 1 (k = 0)
            if k_value >= 1:

                # given this position in the good suffix array isn't filled OR a smaller possible shift position is found 
                # store this in the good suffix array. This is important to ensure shifts aren't aggressive and don't miss any
                # further matches allowing for a smaller, safer shift 
                if (good_suffix_array[k_value] == 0) or (p_value < good_suffix_array[k_value]):
                    good_suffix_array[k_value] = p_value

    # fill up empty values to store valid, safe shifts in the right to left direction
    # the logic lies under the assumption that if a shift position p is safe for a mismatch at position k 
    # then it should also be safe for values smaller than k (unless they already have a SAFER shift position that won't skip mismatches)
    # this helps increase efficiency essentially and in a way helps implement Galil's optimisation by making sure we never re-check 
    # positions which can re-use a safe shift using the good suffix array
    for index in range(size - 1, 1, -1):
        if good_suffix_array[index] != 0 and good_suffix_array[index - 1] == 0:
            good_suffix_array[index - 1] = good_suffix_array[index] 

    good_suffix_array[0] = "Redundant" 

    return good_suffix_array

def matched_prefix_array(pat : str) -> list[int]:
    """
    Function Description: This function constructs the matched prefix array as described in the FIT3155 lecture content 

    Approach Description: The output of this function stores the length of the longest prefix which matches the suffix of 
    the pattern, needed during preprocessing. This implementation follows the standard Boyer Moore matched prefix 
    implementation which is as follows:
        1. Compute the Z Array on the original pattern
        2. Scan the pattern from right to left
        3. Find the longest possible prefix that matches a suffix from the pattern and store it at that given posiiton

    The reason this helper function wasn't modified as compared to the good suffix helper function is to ensure there is still
    a valid fallback in logic if the conditions described in the specifications fail. Since this logic simply aligns the suffix 
    with a prefix of the pattern no further modifications are needed. It will also be used in the event of a full match: " if we find
    a complete match we shift the pattern by m − mp(2) places and this will be explained in tutorials."

    Input: 
        - pat, a string denoting the desired pattern
        - pat, a string denoting the pattern

    Output: matched_prefix_array, a list of integers denoting the length of the longest prefix of the pattern which matches a suffix. This 
    keeps all required values based on 1-based indexing as explained in the lecture content/notes

    Time Complexity Analysis: O(m) where m is the length of the pattern as the pattern is scanned AT MOST once

    Space Complexity Analysis: O(m) where m is the length of the pattern needed for storing the Z Array and matched_prefix_array

    REFERENCE: FIT3155 Lecture Content Week 2 
    """
    size = len(pat)

    zArray = ZAlgorithm(pat) # compute the Z values of the initial pattern 

    matched_prefix_array = [0] * (size + 1) # create the matched prefix array of size + 1 as shown in the lectures

    longest_matched_prefix = 0

    # iterate through the pattern from right to left 
    for index in range(size - 1, -1, -1):
        # determine if a substring of the pattern matches the pattern length (aka reaches the end of the pattern)
        # and update the longest possible matched prefix till this point
        if zArray[index] + index == size:
            longest_matched_prefix = zArray[index]

        # index + 1 ensures 0-based index -> 1-based position (matching the array structure shown in the lectures)
        matched_prefix_array[index + 1] = longest_matched_prefix

    matched_prefix_array[1] = size
    matched_prefix_array[0] = "Redundant"

    return matched_prefix_array

def minimum_p_value_shift_using_k_value_lookup_table(pat: str, good_suffix_array: list[int]) -> list[list[int]]:
    """
    Function Description: This function constructs a 2D lookup tablle of size (m + 1) x 256 construct a 2D array with a depth of 
    |alphabet| to simplify Condition 2 determination, so that during pattern matching the check pat[p − 1] = txt[j + k − 1] can be 
    extracted in constant time 

    Approach Description: The valid shift p based on a mismatch at position k is determined by two conditions:
        1.) pat[k + 1 . . . k + m − p + 1] = pat[p . . . m] - a currently matched region reappears as a suffix of the pattern (this
            has been encoded using the good suffix array which determines the minimum possible position this appears)
        2.) pat[p − 1] = txt[j + k − 1] - the character to the left of a reappearing suffix region in the pattern must match the 
            character at the point of mismatch

    Essentially the 2D array is constructed in a way such that [k_value][character_index] denotes condition 1 and 2. Say we find a mismatch
    in the text at txt[j + k − 1], we already know using the modified good_suffix_rule that for a mismatch at position k a region in the pat[k + 1 ... m]
    reappears as a suffix from pat[p ... m]. If p is non-zero pat[p - 1] will yield a valid character which can be converted to ASCII and compared
    to txt[j + k − 1], and if they're equal the shift is valid. If this condition fails for txt[j + k − 1] this given region in [k_value][character_index] will be 
    0 so we need to shift using another method (ie. matched prefix)

    Input: 
        - pat, a string denoting the pattern
        - good_suffix_array, a list of integers denoting the smallest 1 based index p for the position k 

    Output: k_value_lookup_table, a 2D array of size (m + 1) x |alphabet| where the index [k_value][character_index] stores the mimium possible
    p shift such that Condition 1 and 2 for a mismatch position k and character exists, or otherwise 0 indicating this shift isn't possible

    Time Complexity Analysis: O(m) where m is the length of the pattern as the pattern is scanned once and each previous row is copied 
    over using a constant time operation as the alphabet is fixed to 256 

    Space Complexity Analysis: O(m * |alphabet) where m is the length of the pattern and |alphabet| is the length of the alphabet (ie. 256), as 
    we store a 2D array with dimensions (m + 1) x 256 to store occurrences of the shift positions p 
    """
    size = len(pat)

    k_value_lookup_table = []

    # initialise a 2D array of size m + 1 x 256
    for size_creator in range(size + 1):
        row = [0] * 256
        k_value_lookup_table.append(row)

    # iterate from right to left to scan for possible shift values using the good_suffix_array outcomes 
    # ignoring index 0 as we're assuming 1-based indexed k-values (to follow the lecture content)
    for k_value_index in range(size, 0, -1):
        # if no minimum possible p value is found skip to the next index straight away
        if good_suffix_array[k_value_index] == 0:
            continue 
        
        if k_value_index < size: # this is implemented as a safe measure against index out of bounds errors 
            # 1.) copy the entire previous row in case NO valid p shift is found satisfying conditions 1 AND 2 
            k_value_lookup_table[k_value_index] = k_value_lookup_table[k_value_index + 1][:] 

            minimum_p_value_shift = good_suffix_array[k_value_index]

            # 2.) for condition 2 to be met we need to check pat[p − 1]. This eases our ability to check
            #.    for the instersection of Condition 1 and 2 during pattern matching for the check pat[p − 1] = txt[j + k − 1]
            character_index = ord(pat[minimum_p_value_shift - 1]) 

            # only add this to the 2D array if it doesn't already exist from the copying of the previous row in the array 
            # OR a smaller possible shift position is found This is important to ensure shifts aren't aggressive and don't miss any
            # further matches allowing for a smaller, safer shift 
            if k_value_lookup_table[k_value_index][character_index] == 0 or minimum_p_value_shift < k_value_lookup_table[k_value_index][character_index]:
                k_value_lookup_table[k_value_index][character_index] = minimum_p_value_shift

    return k_value_lookup_table

def modified_boyer_moore(txt : str, pat : str) -> list[int]:
    """
    Function Description: This function implements the modified Boyer Moore algorithm logic needed for question 1 of the FIT3155 
    assignment based on the corresponding specifications. The algorithm functions by scanning the pattern against the text using 
    right to left scanning and finding the leftmost index p > k + 1 based on the modified good suffix rule such that:
        1.) pat[k + 1 . . . k + m − p + 1] = pat[p . . . m] - a currently matched region reappears as a suffix of the pattern (this
            has been encoded using the good suffix array which determines the minimum possible position this appears)
        2.) pat[p − 1] = txt[j + k − 1] - the character to the left of a reappearing suffix region in the pattern must match the 
            character at the point of mismatch

    Approach Description: The algorithm functions as follows:
        1.) Preprocess the pattern by doing the following:
            - modified_good_suffix_rule_array(pat): stores the leftmost shift position p which satisfies condition 1 in the specifications  
              for each mismatch position k
            - matched_prefix_array(pat): stores the legnth of the longest matched prefix, which is to be used as a fallback if the above 
              conditions fail or in the case a full match case is encountered
            - minimum_p_value_shift_using_k_value_lookup_table(pat, good_suffixes): precomputes a 2D lookup table which helps simplify condition 
              2 constraints in constant time by storing the minimum possible shift position for a particular character through ASCII conversions
        2.) Align the pattern to the rightmost end of the text using 0-based indexing 
        3.) At each alignment, scan right to left compare the pattern against the text until a mismatch or full match is found 
            - FULL MATCH: record the match position (1-based) and shift left by the longest PROPER prefix-suffix match denoted by matched_prefix_array[2]
            - MISMATCH: Look up condition1_array[k][txt[j+k-1]] to find leftmost possible shift position for that given character. If it succeeds this position
              will yield a non-zero value (otherwise the shift will be done using matched_prefix_array[k + 1]), and thus the shift will be achieved by calculating 
              p - (k + 1) which in 0-based indexing is p - k
        4. Use galil's rule and keep track of a skip counter to avoid rechecking known matches of the pattern 
        5. Continue this process by recomputing the comparison_pointer until the alignment_index < 0

    Input: 
        - pat, a string denoting the pattern
        - txt, a string denoting the text 

    Output: 
        - valid_matches, a list of integers with the 1 based position matches for output
        - runlog, a list of strings storing each iteration in the required format as stated in the specifications

    Time Complexity Analysis: O(n + m * |alphabet|) (worst case WITH Galil's optimisation) where n is the length of the text, m is the length of the pattern
    and |alphabet| is the length of the alphabet (ie. 256)
        - Preprocessing of the pattern takes O(m * |alphabet|) time to construct the good suffix, matched prefix array arrays as well as the lookup table which 
          has dimensions (m + 1) x 256 
        - Without Galil's optimisation the search phase would be O(n * m) in the worst case as the pattern is re-checked repeatedly with each iteration of the search
          but through this efficiency implementation the search phase keeps track of already matched regions of the text, thus simplifying the operation to roughly O(n) 
          in the worst case 

    Space Complexity Analysis: O(m * |alphabet| + n) where n is the length of the text and m is the length of the pattern, and |alphabet| is the length of the alphabet 
    (ie. 256)
        - Preprocessing the good suffix and matches prefix arrays occupies O(m) space, whilst the lookup table with dimensions (m + 1) x 256 occupies O(m * |alphabet|)
        - To construct the valid_matches array this will occupy at most |matches| which is bounded by the length of the text. This can occur for single character 
          pattern matching single character text repeated n times
        - The runlog array will also occupy at most |iterations| needed to scan the text which is bounded by 1 <= |iterations| <= the length of the text
    """
    text_length = len(txt)
    pattern_length = len(pat)

    # edge cases (pattern is empty and pattern is longer than text)
    if pattern_length == 0:
        return [], []
    if pattern_length > text_length:
        return [], []
    
    # extract the good suffixes and good suffixes (preprocessing)
    good_suffixes = modified_good_suffix_rule_array(pat)
    matched_prefixes = matched_prefix_array(pat)
    condition1_array = minimum_p_value_shift_using_k_value_lookup_table(pat, good_suffixes)

    # output variables 
    valid_matches = []
    runlog = []

    # ensure the pattern and text align during matching, also denoting the 0-based index position 
    # from LEFT TO RIGHT 
    # a b a a
    #     a a
    # alignment_index = 2
    # comparison_pointer = 3 (index)
    # first iteration continues till comparison_pointer = 0 AND search area [2,3] is complete
    alignment_index = text_length - pattern_length 
    
    # galil skip logic: 
    # used to make the algorithm VERY efficient especially in the worst case when the pat matches the entire text 
    # at all points by resetting the comparison pointer in a way such that upon a shift it avoids recomparing/resetting 
    # and thus not needing to compare from the start of pattern repeatedly. It is set upon each match/mismatch in the following way:
    #   - FULL MATCH: Skip the longest matched prefix found using the matched prefix array (or keep it as 0 if the pattern is length 1)
    #     so that in the next alignment the pattern doesn't need to compare from the rightmost character but rather from the next longest 
    #     matched prefix
    #   - MISMATCH:  
    #       1.) Condition 2 fails: Shift by the longest matched proper prefix at that given k_value (or keep it as 0 if the pattern is length 1)
    #           so that in the next alignment the pattern doesn't need to compare from the rightmost character but ratrher from the next longest matched
    #           prefix which in this case is denoted by matched_prefix_array[k + 1]
    #       2.) Condition 2 passes: Shift the pattern by pattern_length - k as this region in the pattern is known to match the text based on 
    #           the rules described, so that in the next alignment the pattern starts comparing from the point of mismatch only since we know 
    #           the region before it already matches with the text which is denoted by pattern_length - final_shift_p
    galil_skip_counter = 0

    # continue the search until the pattern moves past the end of the text 
    while alignment_index >= 0: 
        # for this given alignment calculate the comparison pointer using galil's optimisation
        # (this comparison pointer by the logic og galil's optimisation will decrease as the search continues)
        # as the search window reduces as matches are found
        comparison_pointer = pattern_length - 1 - galil_skip_counter 
        
        # while the comparison_pointer is valid and still spans the search area (see above) continue the search
        while (comparison_pointer >= 0) and (pat[comparison_pointer] == txt[alignment_index + comparison_pointer]): 
            comparison_pointer -= 1 # keep moving left 
            
        # FULL match case at this comparison_pointer
        if comparison_pointer < 0:
            valid_matches.append(alignment_index + 1) # store the 1-based index of the match for the output 

            ### RUNLOG FORMATTING ###
            j = alignment_index # current 0 based alignmemnt index 
            k_plus_1 = 0 # as it's a full match there is NO mismatch

            # identify p value based on matched prefix fallback 
            if pattern_length > 1: 
                p_runlog = matched_prefixes[2] # store the p-value of the next largest PROPER prefix-suffix match that isn't the full pattertn
            else:
                p_runlog = 1 # default shift to 1

            runlog.append(f"{j} {k_plus_1} {p_runlog}") # append to runlog file 
            ##########################

            if pattern_length > 1: # identify safe shift based on matched prefix fallback given the pattern has length > 1
                left_shift = pattern_length - matched_prefixes[2] # as the entire pattern matches shift by the next possible longest prefix-suffix match to ensure safety
                galil_skip_counter = matched_prefixes[2] # avoid the comparison pointer starting from the rightmost character but rather from the next longest proper prefix-suffix match
            else:
                left_shift = 1 # default shift to 1 
                galil_skip_counter = 0 # as the pattern is length 1 the galil_skip needs to be kept 0 so the pattern doesn't skip an occurrence of the text

            alignment_index -= left_shift

        # Mismatch case 
        else:
            k = comparison_pointer + 1  # 1-based mismatch position of mismatch

            # we need to reset the skip counter at this point since we may need to change the entire way the skip counter is implemented after a shift
            # and thus avoid skipping characters that still need to be matched 
            galil_skip_counter = 0 

            # check the character at the mismatch point based on 1-based indexing: txt[j + k − 1] 
            if (alignment_index + k - 1) >= 0: 
                mismatch_character = txt[alignment_index + k - 1]
            else:
                mismatch_character = None
            
            # apply and now check for condition 2
            final_shift_p = 0

            # look up the 2D table using the mismatch position k and the character at the point of mismatch as this table stores the minimum values 
            # which pass condition 1, at this point condition 2 will known to be successful or not dependant on if the final_shift_p is non Zero
            if mismatch_character is not None:
                final_shift_p = condition1_array[k][ord(mismatch_character)]

            ### RUNLOG FORMATTING ###
            j = alignment_index # current 0 based alignmemnt index 
            k_plus_1 = k # current position of k for this iteration 

            # if condition 2 succeeds, log the minimum p value for the shift in 0=based indexing 
            # otherwise use the minimum possible shift 
            if final_shift_p != 0: 
                p_runlog = final_shift_p 
            else:
                p_runlog = 0

            runlog.append(f"{j} {k_plus_1} {p_runlog}")
            ##########################

            # if condition 2 fails fallback to the matched prefix shifting 
            if final_shift_p == 0:
                # given that the already matched range is within the pattern length 
                if k + 1 <= pattern_length:
                    left_shift = pattern_length - matched_prefixes[k + 1] # shift the pattern by longest PROPER prefix-suffix match till the point of mismatch
                    galil_skip_counter = matched_prefixes[k + 1] # the galil shift will now ensure the pattern is analysed from the point of mismatch in the next iteration
                else:
                    # the mismatch may have occurred at the very last character of the pattern (aka rightmost point)
                    left_shift = 1 # default shift to 1 
                    galil_skip_counter = 0 # reset the skip counter to 0 and start from scratch 
                
                alignment_index -= left_shift # shift leftward
            
            else:
                # shift left and align the pattern to another occurrence of a suffix match 
                # shift = p - (k + 1) (1 - based)
                # shift = p - k (0-based)
                alignment_index -= final_shift_p - k
                galil_skip_counter = pattern_length - final_shift_p

    return valid_matches, runlog 

# REFERENCE: Parts of this code snippet was copied from the "Command-line usage tutorial for Assignments"
# document provided in the assignment specifications 
if __name__ == '__main__':

    #retrieve the file paths from the commandline arguments
    _, txt, pat = sys.argv

    txt = read_file(txt)
    pat = read_file(pat)
    matches, runlog = modified_boyer_moore(txt, pat)

    write_output(matches, "output a1q1.txt")
    write_runlog(runlog, "runlog a1q1.txt")
