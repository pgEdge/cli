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

# This 1 at the end is required, even though it looks like an accident :)
1;

