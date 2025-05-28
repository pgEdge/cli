
export pgeMdDir=~/dev/pgedge/cli/help
export nc=../out/posix/pgedge
export output_dir=../docs

modules=(ace cluster db localhost service spock um)

mkdir -p "$output_dir"

write_help() {
  # Generate help for a specific module and its commands
  local module="$1"
  $nc $module --help | sed -r 's/\x1B\[[0-9;]*[mGKH]//g; /^(SYNOPSIS|POSITIONAL ARGUMENTS|DESCRIPTION|FLAGS|COMMANDS)/s/^/## /' > "$output_dir/functions/$module.md";
  
  local commands=()
  # Parse the generated module help file to extract commands
  module_file="$output_dir/functions/$module.md"
  if [[ -f "$module_file" ]]; then
    in_commands=0
    while IFS= read -r line; do
      # Look for the start of the commands section
      if [[ "$line" =~ COMMAND\ is\ one\ of\ the\ following: ]]; then
        in_commands=1
        continue
      fi
      if [[ $in_commands -eq 1 ]]; then
        # Stop if we hit an empty line or a line that doesn't look like a command
        [[ -z "$line" ]] && break
        # Match lines that start with whitespace, then a command, then optional whitespace, then #
          if [[ "$line" =~ ^[[:space:]]*([a-zA-Z0-9_-]+)[[:space:]]*# ]]; then
          cmd="${BASH_REMATCH[1]}"
          commands+=("$cmd")
        fi
      fi
    done < "$module_file"
  fi

  echo "Found commands for module '$module': ${commands[*]}"
  shift
  for cmd in "${commands[@]}"; do
    local fname="${module}-$(echo "$cmd" | tr ' ' '-').md"
    echo "Generating help for module '$module', command '$cmd' -> $fname"

    if ! $nc $module $cmd --help | sed -r 's/\x1B\[[0-9;]*[mGKH]//g; /^(SYNOPSIS|POSITIONAL ARGUMENTS|DESCRIPTION|FLAGS|COMMANDS)/s/^/## /' > "$output_dir/functions/$fname"; then
      echo "ERROR: Failed to generate help for module '$module', command '$cmd'" >&2
    fi
  done
}

index() {
  local index_file="$output_dir/cli_functions.md"
  echo "# CLI Functions" > "$index_file"
  echo "" >> "$index_file"

  for module in "${modules[@]}"; do
    echo "## $module module commands" >> "$index_file"
    echo "" >> "$index_file"
    echo "| Command | Description |" >> "$index_file"
    echo "|---------|-------------|" >> "$index_file"
    # Parse the -module.md file to extract commands and descriptions
    module_file="$output_dir/functions/${module}.md"
    awk -v module="$module" '
      BEGIN { in_commands=0 }
      /COMMAND is one of the following:/ { in_commands=1; next }
      in_commands && /^[[:space:]]*$/ { exit }
      in_commands && /^[[:space:]]*[^[:space:]]/ {
      # Match: <cmd>   # <desc>
      split($0, parts, "#")
      cmd=parts[1]
      gsub(/^[ \t]+|[ \t]+$/, "", cmd)
      desc=parts[2]
      gsub(/^[ \t]+|[ \t]+$/, "", desc)
      if (cmd != "") {
        printf "| [`%s %s`](functions/%s-%s.md) | %s |\n", module, cmd, module, cmd, desc
      }
      }
    ' "$module_file" >> "$index_file"
    echo "" >> "$index_file"
  done
}

############## MAINLINE ############################
if [ $# -ne 1 ]; then
  echo "ERROR: must be one 'module' parameter"
  exit 1
fi

m=$1
if [ "$m" == "all" ]; then
  echo "Generating help for all modules..."
  echo "Removing existing help files..."
  rm -f $output_dir/functions/*

  # Loop through all modules and generate help
  for module in "${modules[@]}"; do
    write_help "$module"
  done

elif [ "$m" == "index" ]; then
  index
else
  echo "Generating help for module '$m'..."

  # Check if the module is valid
  if [[ ! " ${modules[@]} " =~ " ${m} " ]]; then
    echo "ERROR: '$m' is not a valid module. Valid modules are: ${modules[*]}"
    exit 1
  fi
  write_help "$m"
fi
