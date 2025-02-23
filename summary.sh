#!/bin/bash

# Output file name
output_file="project_structure_and_contents.txt"

# Project directory
project_dir="."

# Script file name
script_file="$(basename "$0")"

# Files/directories to exclude (using wildcards for __pycache__ and .git)
exclude_patterns=( "__pycache__/*" ".git/*")

# Files whose contents should be excluded (but listed)
exclude_contents=( "training.log" "$output_file" "$script_file")

# Function to recursively traverse...
traverse_and_output() {
  local dir="$1"
  local indent="$2"

  find "$dir" -mindepth 1 -print0 | while IFS= read -r -d $'\0' file; do
    relative_path="${file#$project_dir/}"

    # Exclude files/directories entirely (do not list)
    exclude_file=false
    for pattern in "${exclude_patterns[@]}"; do
      if [[ "$relative_path" == $pattern ]]; then  # Correct wildcard matching
        exclude_file=true
        break
      fi
    done

    if $exclude_file; then
      continue  # Skip to the next file (do not list at all)
    fi

    # Output the directory/file structure with indentation
    echo -e "${indent}${relative_path}" >> "$output_file"  # List the file/directory

    if [ -f "$file" ]; then
      file_type=$(file -b --mime-type "$file")

      # Check if contents should be excluded (but file listed)
      exclude_content=false
      for pattern in "${exclude_contents[@]}"; do
        if [[ "$relative_path" == "$pattern" ]]; then
          exclude_content=true
          break
        fi
      done

      if ! $exclude_content; then  # Include content only if not in exclude_contents
        if [[ "$file_type" == text/* || "$file_type" == application/json || \
              "$file_type" == application/xml || "$file_type" == application/x-yaml || \
              "$file_type" == application/x-python || "$file_type" == text/x-script.python ]]; then
          echo -e "${indent}  Contents of: $relative_path" >> "$output_file"
          while IFS= read -r line; do
            echo "$line" >> "$output_file"
          done < "$file"
          echo "" >> "$output_file"
        else
          echo -e "${indent}  (Binary or unsupported file type: $file_type - skipping content)" >> "$output_file"
        fi
      fi  # End if !exclude_content
    elif [ -d "$file" ]; then
      traverse_and_output "$file" "  $indent"
    fi
  done
}

echo "Project Structure and File Contents:" > "$output_file"
traverse_and_output "$project_dir" ""

echo "Finished. Output written to $output_file"
