def print_diamond_from_logic(num_lines):
    # 1. Validate the input
    if not 1 <= num_lines <= 100:
        print("Error: Input must be between 1 and 100.")
        return
    
    if num_lines % 2 == 0:
        print(f"Error: The reference pattern's logic creates a single-peak diamond,")
        print(f"which only works for an odd number of lines. You entered {num_lines}.")
        return

    # 2. Set up the source text and size variables
    source_text = "FORMULAQSOLUTIONS"
    n_text = len(source_text)
    mid_point = num_lines // 2

    # 3. Build the upper half of the diamond
    for i in range(mid_point + 1):
        length = 2 * i + 1
        num_spaces = (num_lines - length) // 2
        start_index = i % n_text  # Start index is based on the line number

        # Build the substring, wrapping around the source text
        substring = ""
        for j in range(length):
            substring += source_text[(start_index + j) % n_text]
        print(" " * num_spaces + substring)

    # 4. Build the lower half of the diamond
    for i in range(1, mid_point + 1):
        length = num_lines - 2 * i
        num_spaces = (num_lines - length) // 2
        # The start index for the lower half follows its own rule
        start_index = (mid_point + i) % n_text

        # Build the substring, wrapping around the source text
        substring = ""
        for j in range(length):
            substring += source_text[(start_index + j) % n_text]
        print(" " * num_spaces + substring)

# --- Example Usage ---
print_diamond_from_logic(21)