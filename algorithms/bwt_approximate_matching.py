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

    for position, distance in matches:
        f.write(str(position) + " " + str(distance) + "\n")

    f.close()

def compute_suffix_array(txt: str) -> (str, list[(int, str)], list[int]): 
    """
    Function Description: This function constructs a suffix array of any given text by generating all possible suffixes for that
    given string, sorting them in alphabetical order and then extrating their starting indices to return as a suffix array 

    Approach Description: The function starts by appending the provided text with a terminal "$" character for proper sorting 
    and identification of the end of the string. Then, it generates all possible suffixes of that new text string and their corresponding 
    starting indices in the new text. Then, these suffixes are sorted alphabetically using Python's inbuild sorting function, which from
    there a suffix array is constructed by iterating through this array and extracting the indices of those sorted suffixes 

    Input: txt, a string denoting the input text 

    Output: 
        - new_text, the input string appended with a terminal "$" character
        - text_suffixes: a list of pair tuples containing an (index, suffix) which represents the position and suffixes of the input string 
        - suffix_array: a list of integers denoting the starting indices of all the suffixes in alphabetically sorted order 

    Time Complexity Analysis: IGNORED as stated in specifications 

    Space Complexity Analysis: IGNORED as stated in specifications 
    """
    new_text = txt + "$" # add a flag to mark the end of the string
    text_suffixes = []
    suffix_array = []

    # extract the index and build its corresponding suffix 
    # as per 0 based indexing 
    # index 0 = banana$ (initial string)
    # index 1 = anana$ (1st proper suffixz)
    # ...
    # index 6 = $
    for i in range(len(new_text)):
        suffix = ""         

        for j in range(i, len(new_text)):
            suffix += new_text[j]

        text_suffixes.append([i, suffix]) # store tuple

    # sort the suffixes by accessing the corresponding suffix within the 
    # tuple via indexing text_suffixes(index, suffix)
    text_suffixes.sort(key = lambda suffix: suffix[1])

    # build the suffix array by extracting the corresponding indices from the sorted
    # text_suffixes(index, suffix) to return a suffix array 
    for each_suffix in text_suffixes:
        suffix_index = each_suffix[0]
        suffix_array.append(suffix_index)

    return new_text, text_suffixes, suffix_array

def extract_BWT(new_text: str, suffix_array: list[int]) -> str:
    """
    Function Description: This function constructs the BWT of a string with its provided suffix array 

    Approach Description: The BWT is formed by extracting the character immediately before each character of 
    a provided string (with the exception of the 0th index which wraps to the (n - 1)th index). This simulates 
    the condition of forming the string by the letters that (cyclically) precede those in the first column (F) 
    of M as stated in the FIT3155 lectures 

    Input: 
        - new_text, the input string (assumed to have the terminal character "$" appended already)
        - suffix_array, a list of integers denoting the sorted suffixes, aka. suffix array 

    Output: 
        - BWT_string, a string denoting the BWT of the text 

    Time Complexity Analysis: IGNORED as stated in specifications 

    Space Complexity Analysis: IGNORED as stated in specifications 
    """
    BWT_string = "" 

    # iterate through each index in the suffix array to find its corresponding position in the text
    for index in suffix_array:
        if index == 0: # in the event of wrapping to the $ (imagine a circle we need to reach the end of the tail)
            BWT_string += new_text[len(new_text) - 1]
        else:
            BWT_string += new_text[index - 1] # A BWT is constructed from the F column of a matrix M based on the suffix array 

    return BWT_string

def compute_rank(BWT_string: str) -> list[int]:
    """
    Function Description: This function computes the rank strucutre as defined in the FIT3155 lectures, in which Rank(x)
    denotes the position/starting index where x first appears in the BWT matrix (aka column F)

    Approach Description: The function scans the BWT string and counts the number of occurrences of each unique character
    using its corresponding ASCII value. It then iterates through the possibilities of this array to compute the rank by 
    accumulating a cumulative total to denote the position which is occupied by the given character in the BWT string 

    Input: BWT_string, a string denoting the BWT of the text 

    Output: rank, a list of integers where rank(x) denotes the starting index of a character in the columnn F in the BWT matrix M

    Time Complexity Analysis: O(n + |alphabet|), where n is the length of the BWT string and |alphabet| = 256 (the possible values based on ASCII)
    as you iterate through the length of the BWT string to find the number of occurrences and then iterate through the entire alphabet to 
    compute the rank of each character in the BWT string 

    Space Complexity Analysis: O(|alphabet|), as two arrays of size 256 are used to store the count and rank

    REFERENCE: FIT3155 Applied Week 4 Solutions (Question 5)
    """
    # initialise arrays (frquency keeps count, ranks store the rank of each character in the BWT string)
    frequency = [0] * 256
    rank = [0] * 256 

    # iterate through each character in the BWT string and count the frequency which it occurs 
    for character in BWT_string:
        char_ascii_value = ord(character) # convert to ASCII value to obtain an index within the 256 ASCII range 
        frequency[char_ascii_value] += 1 # iterate the count for this specific character 

    rank[0] = 0 # assume the first character in the ASCII range at index 0 appears first so rank calculations are accurate 
    # this 0 will be carried to the "$" character which occupies ASCII value 36, following the conventions covered in the lectures

    for index in range(1, 256): # start from 1 as index 0's rank is already set to 0
        rank[index] = rank[index - 1] + frequency[index - 1] # copied from the Week 4 Applied Solutions 
        # essentially use the preivous rank and frequency values to compute the new rank

    return rank 

def compute_nOccurences(BWT_string: str) -> list[int]:
    """
    Function Description: This function computes the nOccurrences array as defined in the FIT3155 lecture content, in which nOccurrences(x, BWT[0..i)) 
    denotes the number of times character x appears in BWT[0..i) for any character x till the position i EXCLUSIVE

    Approach Description: Based on the original applied solutions, the pseudocode creates an array in which nOccurrences[i] stores the count of ONLY character x which occurs 
    previously till that point. In this modification we extend this to ensure we keep track of ALL characters x till this point, thus constructing a 2D 
    array. Thus for each position i the previous running counts of ALL characters before this point are stored in the nOccurrences array before the 
    running count for that given character is incremented, ensuring the stored values represent the number of ALL prior occurrences in the BWT

    Input: BWT_string, a string denoting the BWT of the text 

    Output: nOccurrences, a list of integers where nOccurrences[i][x] stores the number of times the character x appears in BWT_string[0..i)

    Time Complexity Analysis: O(n * |alphabet|) where n is the length of the BWT_string and alphabet| = 256 for ASCII, as this string is scanned
    once BUT at each iteration the previous values are copied over to construct the 2D matrix structure 

    Space Complexity Analysis: O(n * |alphabet|), where n is the length of the BWT string and |alphabet| = 256 for ASCII as arrays of these 
    respective lengths are used in the function to construct an array of size (n + 1) x 256. The array is of size n + 1 than n because the 
    during pattern matching searching, the update rule for ep requires indexing at ep + 1. As ep can be at most n - 1 ep + 1 can reach n in 1-based indexing, 
    so the array must have a valid row at index n to prevent index out of range errors

    REFERENCE: FIT3155 Applied Week 4 Solutions (Question 6) BUT extended from 1D to a 2D structure 
    """
    size = len(BWT_string)

    nOccurrences = []

    # initialise a 2D array of size m + 1 x 256, the reason for the array being of size m + 1 is to account for the ep + 1 indexing during pattern matching, 
    # as ep can be at most m - 1 so ep + 1 can reach m in 0-based indexing
    for size_creator in range(size + 1):
        row = [0] * 256
        nOccurrences.append(row)

    # iterate through the BWT string
    for index in range(len(BWT_string)):
        # extract the current character and its correpsonding ASCII value
        current_char = BWT_string[index]
        char_ascii_value = ord(current_char)

        nOccurrences[index + 1] = nOccurrences[index][:] # copy the entire previous row so all character counts are carried forward from the previous iteration
        # this is the main modification from the original pseudocode to create a 2D array structure 

        nOccurrences[index + 1][char_ascii_value] += 1 # increment only the current character's count for this new row

    return nOccurrences

def backward_search_exact_match_case(pat, suffix_array, ranks, occurrences):
    """
    Function Description: This function performs exact pattern matching on a given text based on the FIT3155 Lecture content
    by using the BWT constructed using the suffix array and matrix M to analyse the pattern, and return all possible positions 
    in the text where the pattern occurs exactly. It does this by narrowing the range of sp and ep such that this interval
    contains the positions of the pattern exactly within the text 

    Approach Description: The function uses a preprocessed suffix array, rank and nOccurrences array to perform a search in a backward
    direction, iteratively narrowing the sp, ep range by applying the update rules taught in the FIT3155 Lectures such that when the function
    ends the resulting range of sp, ep corresponds to the exact match positions in the text. If the pattern cannot be found in the text 
    the final_result array will return nothing as the sp, ep range will fail due to sp > ep 

    Input: 
        - pat, a string denoting the pattern to be searched
        - suffix_array, a list of integers denoting the starting indices of all suffixes in sorted order
        - ranks, a list of integers where rank(x) denotes the starting index of a character in the columnn F in the BWT matrix M
        - occurrences, nOccurrences, a list of lists where nOccurrences[i][x] stores the number of times the character x appears in BWT_string[0..i]

    Output: 
        - final_matches, a list of integers containng the indices where the pattern occurs exactly within the text 

    Time Complexity Analysis: O(m + multiplicty) where m is the length of the pattern and multiplicity is the number of exact matches found 
        - The backward search iterates through the length of the pattern right to left to update the sp, ep range 
        - After the search has been completed the resultant sp, ep range is used to iterate through the suffix array and note down the positions
        in which the pattern exists in the text, such that the matches correspond to ep - sp + 1

    Space Complexity Analysis: O(multiplcity), where multiplicity is the number of exact matches found
        - The function constructs a final_matches array of length multiplcity to store the positions in which the pattern matches the text
    """
    pattern_length = len(pat)

    # edge case for an empty pattern
    if pattern_length == 0:
        return []

    # initialise sp and ep points based on 0-based indexing 
    # the sp, ep range represents the matching suffixes at a given point 
    sp = 0
    ep = len(suffix_array) - 1 # ensures the index of the last possible position in the suffix array is included in the search array considering 
    # 0-based indexing 

    for character in range(pattern_length - 1, -1, -1): # iterate right to left in the pattern considereing 0-based indexing
        # extract the current characters ASCII value 
        character_index = ord(pat[character]) 

        # update sp and ep based on the rules taught in the lecture NOTING the difference
        # that the nOccurrences table stores the nOccurrences of EVERY character of the pat  
        # before the current character index
        sp = ranks[character_index] + occurrences[sp][character_index]
        ep = ranks[character_index] + occurrences[ep + 1][character_index] - 1 # ep + 1 =  L[1...ep] in 0-based indexing 

        # pattern matching fails
        if sp > ep:
            return []

    final_matches = []

    # at this point sp,ep contain all possible suffixes which match the ENTIRE pattern so 
    # extract their positions using the final sp, ep range 
    for character in range(sp, ep + 1):
        final_matches.append(suffix_array[character])

    return final_matches

"""
REFERENCE: This solution is partially inspired by this research paper: https://academic.oup.com/bioinformatics/article/25/14/1754/225615
The branching assumption approach used below is inspired by the backtracking tree exploration idea described in:
Li H. and Durbin R. (2009)'s research 

MATCH DISTANCE 1 RATIONALE: This provides a higher level overview of the thinking behind the below functions 
for each possible match distance 1 case

For each of the below functions we assume 2 outcomes at that given character in the pattern as we scan from 
right to left (as taught in the lectures):
    - Assumption 1: At this given character in the pattern it corresponds to an exact match in the text 
    - Assumption 2: At this given character in the pattern it corresponds to a mismatch that can be solved 
    via substitution, insertion, deletion or transposition

We treat these assumptions as possible branching search outcomes and narrow the sp, ep range differently and 
then discard them if they fail at a given point (sp > ep)

These branches are stored using a stack based array which stores the following information:
    - pattern_index: The current character of the pattern being searched
    - sp: The current sp value
    - ep: The current ep value
    - error_token: Whether the match distance has been identified 
"""

def backward_search_with_substitution_case(pat, suffix_array, ranks, occurrences):
    """
    Function Description: This function finds all positions in the text such that the pattern matches the text by substituting 
    exactly one character at a specified position in the pattern

    Approach Description: The function uses a stack based search of the pattern from right to left using the rationale describe above,
    specifically by assuming an exact pattern match and substitution case at a given position in the pattern. The substitution case
    tries every possible character except the current character at that position, to narrow the sp, ep range and mock the scenario in which
    the character was substituted by another character at that given positon in the pattern and then applying the error_token indicating a match distance 
    of 1. Once spent, only the exact match assumption condition continues for the remaining pattern positions.

    This will eventually return all positions in which the pattern matches the text with a match distance of 1 by substitution, as at each position we explore 
    the possibility of a substitution

    Input: 
        - pat, a string denoting the pattern to be searched
        - suffix_array, a list of integers denoting the starting indices of all suffixes in sorted order
        - ranks, a list of integers where rank(x) denotes the starting index of a character in the columnn F in the BWT matrix M
        - occurrences, nOccurrences, a list of integers where nOccurrences[i] stores the number of times BWT_string[i] appears in BWT_string[0..i)

    Output: 
        - final_matches, a list of integers containng the indices where the pattern matches the text using 1 substitution

    Time Complexity Analysis: O(m * |alphabet|) where m is the length of the pattern and |alphabet| is the length of the alphabet (ie. 256)
        - At each pattern position assuming an exact match assumption the update of the sp, ep range takes O(1) time continuing for every letter
        of the pattern
        - At each pattern position assuming a substitution case there is at most |alphabet| - 1 possibliities as you try every character that is NOT 
        the current character in the pattern 

    Space Complexity Analysis: O(m * |alphabet| + multiplicity) where m is the length of the pattern, |alphabet| is the length of the alphabet (ie. 256)
    multiplicity is the number of exact matches found 
        - The stack stores at most O(m x |alphabet|) states since at each position at most |alphabet| substitutions can occur
        - The function constructs a final_matches array of length multiplcity to store the positions in which the pattern matches the text
    """
    pattern_length = len(pat)

    # edge case in which the pattern is empty 
    if pattern_length == 0:
        return []

    # save the initial variables for the array based stack
    current_pattern_index = pattern_length - 1 # noting 0-based indexing # noting 0-based indexing
    initial_sp = 0 
    initial_ep = len(suffix_array) - 1 # ensures the index of the last possible position in the suffix array is included in the search array considering 
    # 0-based indexing 
    error_token = 0 # we haven't encountered any substitution cases 

    # start with this in the stack
    search_stack = [(current_pattern_index, initial_sp, initial_ep, error_token)]

    matches = []

    # search for substitution cases from left to right 
    while len(search_stack) > 0:
        pattern_index, sp, ep, error_token = search_stack.pop() # pop the last added state in the stack and explore this branching outcome # pop the last added state in the stack and explore this branching outcome

        # if the entire pattern is searched, all positions in the range of sp and ep represents the positions 
        # where a substitution case an occur
        if pattern_index < 0:
            for index in range(sp, ep + 1):
                matches.append(suffix_array[index])

            continue 

        # extract the current character and original sp, ep before we consider assumptions 
        current_character = ord(pat[pattern_index])
        original_sp = sp
        original_ep = ep

        # ASSUME a full match occurs at this position => narrow sp, ep and move on without spending the error token
        new_sp = ranks[current_character] + occurrences[original_sp][current_character]
        new_ep = ranks[current_character] + occurrences[original_ep + 1][current_character] - 1

        # check if the next character is valid as per the pattern matching process adding it to the stack,
        # or otherwise discard this possiblity 
        if new_sp <= new_ep:
            search_stack.append((pattern_index - 1, new_sp, new_ep, error_token))

        # ASSUME a substitution occurs at this position => narrow sp, ep and move on spending the token given it hasn't been
        # used till this point 
        if error_token == 0:
            for possible_char in range(256): # skip the current character to see possiblities where a substuted character can take its place 
                if possible_char != current_character:
                    new_sp = ranks[possible_char] + occurrences[original_sp][possible_char]
                    new_ep = ranks[possible_char] + occurrences[original_ep + 1][possible_char] - 1

                    # if the range is valid as per the pattern matching process, store the shift and use the error token 
                    # indicating a substitution case is possible (creating a new set of branches)
                    if new_sp <= new_ep:
                        search_stack.append((pattern_index - 1, new_sp, new_ep, 1))

    return matches 

def backward_search_with_deletion_case(pat, suffix_array, ranks, occurrences):
    """
    Function Description: This function finds all positions in the text such that the pattern matches the text by deleting 
    exactly one character at a specified position in the pattern 

    Approach Description: The function uses a stack based search of the pattern from right to left using the rationale describe above,
    specifically by assuming an exact pattern match and deletion case at the given position in the pattern. The deletion case skips the 
    current pattern character (by assuming it doesn't exist at that given position in the text) and retaining the current sp, ep range 
    to then continue the search again from the next character, whlile applying the error_token to indicate an edit distance of 1. Once spent 
    only the exact match assumption assumption continues for the remaining pattern positions

    Input: 
        - pat, a string denoting the pattern to be searched
        - suffix_array, a list of integers denoting the starting indices of all suffixes in sorted order
        - ranks, a list of integers where rank(x) denotes the starting index of a character in the columnn F in the BWT matrix M
        - occurrences, nOccurrences, a list of integers where nOccurrences[i] stores the number of times BWT_string[i] appears in BWT_string[0..i)

    Output: 
        - final_matches, a list of integers containng the indices where the pattern matches the text using 1 deletion

    Time Complexity Analysis: O(m) where m is the length of the pattern
        - At each pattern position assuming an exact match assumption the update of the sp, ep range takes O(1) time continuing for every letter
        of the pattern
        - The deletion case adds one more additional search state per position by assuming a deletion at that position, retaining the current sp, ep 
        range and moving to the next character 

    Space Complexity Analysis: O(m + multiplicity) where m is the length of the pattern and multiplicity is the number of exact matches found 
        - The stack stores at most O(m) states since at each position at most 1 deletion assumption can occur
        - The function constructs a final_matches array of length multiplcity to store the positions in which the pattern matches the text
    """
    pattern_length = len(pat)

    # edge case in which the pattern is empty 
    if pattern_length == 0:
        return []

    # noting 0-based indexing 
    current_pattern_index = pattern_length - 1 # noting 0-based indexing 
    initial_sp = 0 
    initial_ep = len(suffix_array) - 1 # ensures the index of the last possible position in the suffix array is included in the search array considering 
    # 0-based indexing 
    error_token = 0 # we haven't encountered any deletion cases 

    search_stack = [(current_pattern_index, initial_sp, initial_ep, error_token)]

    matches = []

    # search for deletion cases from left to right 
    while len(search_stack) > 0:
        pattern_index, sp, ep, error_token = search_stack.pop() # pop the last added state in the stack and explore this branching outcome

        # if the entire pattern is searched, all positions in the range of sp and ep represents the positions 
        # where the full pattern appears
        if pattern_index < 0:
            for index in range(sp, ep + 1):
                matches.append(suffix_array[index])

            continue # break out of the loop

        # extract the current character and original sp, ep before we consider assumptions 
        current_character = ord(pat[pattern_index])
        original_sp = sp
        original_ep = ep

        # ASSUME a full match occurs at this position => narrow sp, ep and move on without spending the error token
        new_sp = ranks[current_character] + occurrences[original_sp][current_character]
        new_ep = ranks[current_character] + occurrences[original_ep + 1][current_character] - 1

        # check if the next character is valid as per the pattern matching process
        # or otherwise discard this possiblity 
        if new_sp <= new_ep:
            search_stack.append((pattern_index - 1, new_sp, new_ep, error_token))

        # ASSUME a deletion occurs at this position => move on spending the token given it hasn't been used
        # till this point, keeping original sp, ep range as we're assuming it never existed in the first place 
        if error_token == 0:
            search_stack.append((pattern_index - 1, original_sp, original_ep, 1))

    return matches

def backward_search_with_insertion_case(pat, suffix_array, ranks, occurrences):
    """
    Function Description: This function finds all positions in the text such that the pattern matches the text by inserting 
    exactly one character at a specified position in the pattern 

    Approach Description: The function uses a stack based search of the pattern from right to left using the rationale describe above,
    specifically by assuming an exact pattern match and insertion case at the given position in the pattern. The insertion case tries every possible
    character in the alphabet and using its ASCII value to further narrow the sp, ep range to simulate the text having an extra character at that given
    pattern position, BUT ensuring the pattern index stays the same to mimic the scenario of an inserted character before continuing the search outcomes 
    and then applying the error_token indicating a match distance  of 1. Once spent, only the exact match assumption condition continues for the remaining pattern 
    positions

    There is also an edge case to be handled such that the inserted character is at the VERY end of the pattern. As this extra character only 
    becomes visible after the entire pattern is consumed, an additional insertion check needs to be performed using the final sp, ep range to account 
    for this case

    Input: 
        - pat, a string denoting the pattern to be searched
        - suffix_array, a list of integers denoting the starting indices of all suffixes in sorted order
        - ranks, a list of integers where rank(x) denotes the starting index of a character in the columnn F in the BWT matrix M
        - occurrences, nOccurrences, a list of integers where nOccurrences[i] stores the number of times BWT_string[i] appears in BWT_string[0..i)

    Output: 
        - final_matches, a list of integers containng the indices where the pattern matches the text using 1 insertion

    Time Complexity Analysis: O(m * |alphabet|) where m is the length of the pattern and |alphabet| is the length of the alphabet (ie. 256)
        - At each pattern position assuming an exact match assumption the update of the sp, ep range takes O(1) time continuing for every letter
        of the pattern
        - At each pattern position assuming a insertion case there is at most |alphabet| possibliities as you try every character is used to assume 
        an insertion 
        - The above statement also applies to the edge case check 

    Space Complexity Analysis: O(m * |alphabet| + multiplicity) where m is the length of the pattern, |alphabet| is the length of the alphabet (ie. 256)
    multiplicity is the number of exact matches found 
        - The stack stores at most O(m x |alphabet|) states since at each position at most |alphabet| insertions can occur
        - The function constructs a final_matches array of length multiplcity to store the positions in which the pattern matches the text
    """

    pattern_length = len(pat)

    if pattern_length == 0:
        return []

    # noting 0-based indexing 
    current_pattern_index = pattern_length - 1 # noting 0-based indexing 
    initial_sp = 0 
    initial_ep = len(suffix_array) - 1 # ensures the index of the last possible position in the suffix array is included in the search array considering 
    # 0-based indexing 
    error_token = 0 # we haven't encountered any transposition cases 

    search_stack = [(current_pattern_index, initial_sp, initial_ep, error_token)]

    matches = []

    # search for insertion cases from left to right 
    while len(search_stack) > 0:
        pattern_index, sp, ep, error_token = search_stack.pop() # pop the last added state in the stack and explore this branching outcome

        # if the entire pattern is searched, all positions in the range of sp and ep represents the positions 
        # where the full pattern appears
        if pattern_index < 0:
            for index in range(sp, ep + 1):
                matches.append(suffix_array[index])

            # ASSUME THE EDGE INSERTION CASE: An extra character is inserted at the very left of the pattern
            # so we need to add one more insertion calculation, using the final sp,ep range 
            # this branch is only considered if the error token hasn't been used yet, as we can still have a match distance of 1
            if error_token == 0:
                # try every possible inserted character which can occur
                for possible_char in range(256):
                    new_sp = ranks[possible_char] + occurrences[sp][possible_char]
                    new_ep = ranks[possible_char] + occurrences[ep + 1][possible_char] - 1

                    # check if the next character is valid as per the pattern matching process, storing the shift
                    # and extracting all matches in the new sp, ep range if valid immediately since the error_token has been used
                    if new_sp <= new_ep:
                        for index in range(new_sp, new_ep + 1):
                            matches.append(suffix_array[index])

            continue # break out of the loop

        # extract the current character and original sp, ep before we consider assumptions 
        current_character = ord(pat[pattern_index])
        original_sp = sp
        original_ep = ep

        # ASSUME a full match occurs at this position = narrow sp, ep and move on without spending the error token
        new_sp = ranks[current_character] + occurrences[original_sp][current_character]
        new_ep = ranks[current_character] + occurrences[original_ep + 1][current_character] - 1

        # check if the next character is valid as per the pattern matching process, storing the shift
        if new_sp <= new_ep:
            search_stack.append((pattern_index - 1, new_sp, new_ep, error_token))

        # ASSUME a insertion occurs at this position = stay at the same place and spending the token given it hasn't been used
        # till this point, to indicate the presence of an extra character in the text
        if error_token == 0:
            # try every possible inserted character which can occur
            for possible_char in range(256):
                new_sp = ranks[possible_char] + occurrences[original_sp][possible_char]
                new_ep = ranks[possible_char] + occurrences[original_ep + 1][possible_char] - 1

                # if the range is valid as per the pattern matching process, store the shift and consume the error token 
                # indicating a insertion case is possible 
                if new_sp <= new_ep:
                    search_stack.append((pattern_index, new_sp, new_ep, 1))

    return matches

def backward_search_with_transposition_case(pat, suffix_array, ranks, occurrences):
    """
    Function Description: This function finds all positions in the text such that the pattern matches the text by swapping  
    two adjacent characters in the text at that given position in the pattern 

    Approach Description: The function uses a stack based search of the pattern from right to left using the rationale describe above,
    specifically by assuming an exact pattern match and transposition case at the given position in the pattern. The transposition case assumes 
    that the character at pat[current_pattern_index - 1] and pat[current_pattern_index] are swapped, so it processes the pat[current_pattern_index - 1]
    first and then the pat[current_pattern_index], esentially narrowing the sp, ep range given at both points in order to update the sp, ep range given it's possible
    (ie. sp > ep), and moving left to pat[current_pattern_index - 2] and consuming an error_token since the previous 2 characters have already been processed. Once 
    spent, only the exact match assumption condition continues for the remaining pattern positions

    Input: 
        - pat, a string denoting the pattern to be searched
        - suffix_array, a list of integers denoting the starting indices of all suffixes in sorted order
        - ranks, a list of integers where rank(x) denotes the starting index of a character in the columnn F in the BWT matrix M
        - occurrences, nOccurrences, a list of integers where nOccurrences[i] stores the number of times BWT_string[i] appears in BWT_string[0..i)

    Output: 
        - final_matches, a list of integers containng the indices where the pattern matches the text using 1 transposition

    Time Complexity Analysis: O(m) where m is the length of the pattern 
        - At each pattern position assuming an exact match assumption the update of the sp, ep range takes O(1) time continuing for every letter
        of the pattern
        - The transposition assumption case performs at most 2 sp, ep range updates per position which is also O(1) time 

    Space Complexity Analysis: O(m + multiplicity) where m is the length of the pattern and multiplicity is the number of exact matches found 
        - The stack stores at most O(m) states since at each position at most 1 transposition assumption can occur
        - The function constructs a final_matches array of length multiplcity to store the positions in which the pattern matches the text
    """
    pattern_length = len(pat)

    if pattern_length == 0:
        return []

    # noting 0-based indexing 
    current_pattern_index = pattern_length - 1 # noting 0-based indexing 
    initial_sp = 0 
    initial_ep = len(suffix_array) - 1 # ensures the index of the last possible position in the suffix array is included in the search array considering 
    # 0-based indexing 
    error_token = 0 # we haven't encountered any transposition cases 

    search_stack = [(current_pattern_index, initial_sp, initial_ep, error_token)]

    matches = []

    # search for transposition cases from left to right 
    while len(search_stack) > 0:
        pattern_index, sp, ep, error_token = search_stack.pop() # pop the last added state in the stack and explore this branching outcome

        # if the entire pattern is searched, all positions in the range of sp and ep represents the positions 
        # where the full pattern appears
        if pattern_index < 0:
            for index in range(sp, ep + 1):
                matches.append(suffix_array[index])

            continue # break out of the loop

        # extract the current character and original sp, ep before we consider assumptions 
        current_character = ord(pat[pattern_index])
        original_sp = sp
        original_ep = ep

        # ASSUME a full match occurs at this position = narrow sp, ep and move on without spending the error token
        new_sp = ranks[current_character] + occurrences[original_sp][current_character]
        new_ep = ranks[current_character] + occurrences[original_ep + 1][current_character] - 1

        # check if the next character is valid as per the pattern matching process, storing the shift
        if new_sp <= new_ep:
            search_stack.append((pattern_index - 1, new_sp, new_ep, error_token))

        # ASSUME a transposition occurs at this position meaning 2 adjacent characters are swapped in the text =
        # interpret index - 1 first then index, spending the token and moving to the pattern_index - 2th character
        # check the error token hasn't been used till this point, the pattern index is still valid and 
        # the two adjacent characters are distinct
        if (error_token == 0) and (pattern_index > 0) and (pat[pattern_index] != pat[pattern_index - 1]):
            # extract the previous character and calculate new sp, ep range (assuming it came first)
            previous_character = ord(pat[pattern_index - 1]) 

            previous_character_sp = ranks[previous_character] + occurrences[original_sp][previous_character]
            previous_character_ep = ranks[previous_character] + occurrences[original_ep + 1][previous_character] - 1

            # check if the previous characte ep, ep range is valid as per the pattern matching process, storing the shift
            if previous_character_sp <= previous_character_ep:
                # calculate the sp, ep range for the current character 
                current_character_sp = ranks[current_character] + occurrences[previous_character_sp][current_character]
                current_character_ep = ranks[current_character] + occurrences[previous_character_ep + 1][current_character] - 1

                # check if the current character sp, ep range is valid as per the pattern matching process, storing the shift
                # and indicating a valid transposition case
                if current_character_sp <= current_character_ep:
                    # skip two positions and spend the error token
                    search_stack.append((pattern_index - 2, current_character_sp, current_character_ep, 1))

    return matches

def backward_search_with_less_than_distance_1_cases(pat, suffix_array, ranks, occurrences):
    """
    Function Description: This function finds all positions in the text where the pattern matches with a match distance of <= 1
    by combining exact matches (distance 0) and all distance 1 match cases (substitution, deletion, insertion, transposition) 

    Approach Description: The function first runs the exact match search and records all distance 0 positions into the final_results array. 
    It then runs each of the four distance 1 search functions and based on the logic described above stores these positions in the final_results_array
    GIVEN that position has already not been recorded. The final_results_array is then scanned in order to produce the output based on 1-based
    indexing 

    Input: 
        - pat, a string denoting the pattern to be searched
        - suffix_array, a list of integers denoting the starting indices of all suffixes in sorted order
        - ranks, a list of integers where rank(x) denotes the starting index of a character in the columnn F in the BWT matrix M
        - occurrences, nOccurrences, a list of integers where nOccurrences[i] stores the number of times BWT_string[i] appears in BWT_string[0..i)

    Output: 
        - final_matches, output, a list of tuples (position, distance) where position is the 1-based index in the text and distance is 0 for exact 
        matches and 1 for distance 1 matches

    Time Complexity Analysis: O(m x |alphabet| + n + occ) where m is the length of the pattern, n is the length of the text, |alphabet| is the alphabet size = 256 
    and occ is the total number of matches found
        - Each of the five search functions runs in O(m x |alphabet|) in the worst case (specifically insertion and substitution cases)
        - Recording results into final_results is O(occ) as based on the search functions as each match found is recorded into the array
        - Scanning final_results to build the output is O(n) as the entire text needs to be scanned to analyse the pattern positions 

    Space Complexity Analysis: O(n + occ) where n is the length of the text and occ is the number of matches
        - The final_results array occupies O(n) space for the entire length of the text
        - The distance_1_matches array occupies O(occ) space as per the search outcomes created from the helper functions
    """
    pattern_length = len(pat)
    text_length = len(suffix_array) - 1 # 0-based indexing

    # distance definitons:
    # None = no match found
    # 0 = exact match found
    # 1 = distance 1 match 
    final_results = [None] * text_length 

    # handle distance 0 exact matches first
    distance_0_matches = backward_search_exact_match_case(pat, suffix_array, ranks, occurrences)

    # filter out every possible distance 0 
    for pattern_index in distance_0_matches:
        # ignore position that denotes the $ character index as the suffix array includes the index of the $ character which is not part 
        # of the original text
        if pattern_index < text_length: 
            final_results[pattern_index] = 0 

    # handle distance 1 match possibilities using the defined helper functions
    distance_1_matches = []
    distance_1_matches += backward_search_with_substitution_case(pat, suffix_array, ranks, occurrences)
    distance_1_matches += backward_search_with_deletion_case(pat, suffix_array, ranks, occurrences)
    distance_1_matches += backward_search_with_insertion_case(pat, suffix_array, ranks, occurrences)
    distance_1_matches += backward_search_with_transposition_case(pat, suffix_array, ranks, occurrences)

    # filter out every possible distance 1
    for position in distance_1_matches:
        # ignore position that denotes the $ character index as the suffix array includes the index of the $ character which is not part 
        # of the original text
        if position < text_length: 
            if final_results[position] is None: # if the position doesn't already occupy an entry from the distance 0 matches add in the distance 1 match
                final_results[position] = 1

    final_matches = []

    # collect the results in order and convert it into 1-based indexing for the output
    for position in range(text_length):
        if final_results[position] is not None:
            final_matches.append((position + 1, final_results[position]))

    return final_matches

# REFERENCE: Parts of this code snippet was copied from the "Command-line usage tutorial for Assignments"
# document provided in the assignment specifications 
if __name__ == '__main__':

    # retrieve the file paths from the commandline arguments
    _, txt_file, pat_file = sys.argv

    txt = read_file(txt_file)
    pat = read_file(pat_file)

    new_text, suffixes, suffix_array = compute_suffix_array(txt)
    BWT_string = extract_BWT(new_text, suffix_array)
    ranks = compute_rank(BWT_string)
    occurrences = compute_nOccurences(BWT_string)

    final_matches = backward_search_with_less_than_distance_1_cases(pat, suffix_array, ranks, occurrences)

    write_output(final_matches, "output_a1q2.txt")

