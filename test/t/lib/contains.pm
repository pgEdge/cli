# The contains subroutine takes two arguments: array and search_term.  contains checks to see if array contains
# a searchable value; if it doesn't, contains returns fail. If it does contain a value, look for search_term
# in array. If array is not empty and the search_term is there, return pass, else, return fail.
#
# To use this subroutine, include the following use statements:
# use lib './t/lib';
# use contains;
# Then, the code at the end of the test (where we actually check for pass/fail) is much like it was before:
# if (contains(@$haystack, "needle"))
# {
#     exit(0);
# }
# else
# {
#     exit(1);
# }
#
# Where haystack is the name of the xxxxx_buf array we're searching, and needle is the literal search term we're looking for.


sub contains
{
    my $haystack = shift;
    my $needle = shift ;

    print("haystack = ($haystack)\n");
    print("needle = ($needle)\n");

    if (!defined $haystack)
    {
        return(0);
    }

    if (!defined $needle)
    {
        return(0);
    }

    if (length($haystack) == 0)
    {
        return(0);
    }

    if (length($needle) == 0)
    {
        return(0);
    }

    if(index($haystack, $needle) != -1)
    {
        print("Haystack and needle both have content, and our value is found - this case correctly returns true\n");
        return(1);
    }
    else
    {
        print("Haystack and needle both have content, but our value is not found - returning 0 as it should\n");
        return(0);
    }
}

# This function takes an input of the standard output buffer of the ctl um list command 
# and traverses through each row to find both the component name (passed as paraemter) and  
# the word Installed in the same line. Returns 1 if its able to find both (indicating the component is installed)
# otherwise 0.

sub is_umlist_component_installed {
    my ($stdout_ref, $component) = @_;

    for my $line (split /\r?\n/, join("\n", @$stdout_ref)) {
        #print "Line : $line\n"; # Print each line with line number

        if ($line =~ /\b$component\b/i && $line =~ /\bInstalled\b/) {
            print("$component is listed as installed.\n");
            return 1; # True, both component and "Installed" found in the same line
        }
    }
    print("$component is NOT Installed\n");
    return 0; # False, either component or "Installed" not found in the same line
}

# This function runs a shell command passed through its first parameter e.g. ctl commands, psql commands
# and returns various err/out buffers. Incase of an issue it prints the various buffers to help with debugging.
# This function helps avoid redundant code (checking for success/buffers and debug prints). 

sub run_command {
    my ($cmd) = @_;
    my ($success, $error_message, $full_buf, $stdout_buf, $stderr_buf) = IPC::Cmd::run(command => $cmd, verbose => 0);

    if (!defined($success)) {
        print "Error executing command: $error_message\n";
        print "Full Buffer output: @$full_buf\n";
        print "Stdout Buffer output: @$stdout_buf\n";
        print "Stderr Buffer output: @$stderr_buf\n";
    }

    return ($success, $error_message, $full_buf, $stdout_buf, $stderr_buf);
}

# This function is similar to the run_command and executes a command passed in its first parameter e.g. ctl commands, psql commands
# and returns various err/out buffers. Incase of an issue it however also performs an exit 1. 
# This function helps avoid redundant code (checking for success/buffers and exiting accordingly). 

sub run_command_and_exit_iferr {
    my ($cmd) = @_;
    my ($success, $error_message, $full_buf, $stdout_buf, $stderr_buf) = run_command($cmd);

    if (!$success) {
        print "Exiting due to command failure: $cmd\n";
        exit(1);
    }

    return ($success, $error_message, $full_buf, $stdout_buf, $stderr_buf);
}


use JSON;

# Retrieves the value of a specified attribute for a given component from a JSON array.
# Takes an JSON-encoded string (e.g. output of ctl info --json), The value of the "component" 
# attribute to match (e.g. pg16) and the name of the attribute (e.g. status) whose value is to be retrieved.  
# Returns the value of the specified attribute for the matching component, or -1
#  if the component or attribute is not found.
#


sub get_json_component_attribute_value {
    my ($json_str, $component, $attribute) = @_;

    my $json = eval { decode_json($json_str) };
    if ($@) {
        warn "JSON Decoding Error: $@\n";
        return '';
    }

    foreach my $item (@$json) {
        if ($item->{component} eq $component || exists $item->{$attribute}) {
            my $value = $item->{$attribute};
            return defined $value ? $value : '';
        }
    }

    return -1; # Indicates that either the component or attribute was not found
}




# This 1 at the end is required, even though it looks like an accident :)
1;

