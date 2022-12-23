
PFILE=""
COMPONENT="no"
PAGE_TITLE=""
PAGE_DESC=""

def print_file(pOut, pOptFile=""):
   global PFILE
   if pOptFile == "":
     pOptFile = PFILE
   with open('html/' + pOptFile + '.html', 'a') as file:
     file.write(pOut)


def print_header():
  global PAGE_TITLE, PFILE, PAGE_DESC

  title = "OSCG: " + PAGE_TITLE
  string = \
"""
<!-------------   _header()  ------------------------>
<head>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-1BmE4kWBq78iYhFldvKuhfTAU6auU8tT94WrHftjDbrCEXSU1oBoqyl2QvZ6jIW3" crossorigin="anonymous">

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-ka7Sk0Gln4gmtz2MlQnikT1wXgYsOg+OMhuP+IlRH9sENBO0LRn5q+8nbTov4+1p" crossorigin="anonymous"></script>

<script>
function copyToClipboard(text) {
    var sampleTextarea = document.createElement("textarea");
    document.body.appendChild(sampleTextarea);
    sampleTextarea.value = text;
    sampleTextarea.select();
    document.execCommand("copy");
    document.body.removeChild(sampleTextarea);
}

function myFunction(element){
    var copyText = document.getElementById(element);
    copyToClipboard(copyText.value);
}
</script>
"""

  print_file(string)

  print_multilevel_head()

  string = \
"""
<title>
""" + title + \
"""
</title>
</head>

"""
  print_file(string)

  print_multilevel_menu()

  string = \
    "<br>\n" + \
    "<table><tr> \n" + \
    "  <td><img src=img/" + PFILE + ".png height=40 width=125 /></td> \n" + \
    "  <td><h4><font color=black><i>" + PAGE_DESC + "</i></font></h4></td> \n" + \
    "</tr></table>"
  print_file(string)

  return


def print_intro():
  print_file(
"""
OSCG-IO is an Open Source cross-platform installation, configuration & operations framework for datastores.
We fully embrace core PostgreSQL and its extensive collection of enterprise-class community extensions.
We understand that the Postgres worldwide takeover may never be complete, so we support other datastores as well. :-)
"""
)


def print_footer(pOptFile=""):
  print_file(
"""
<!-------------   _footer()  ------------------------>
<table class=table>
  <thead><td colspan=2>&nbsp;</rs></tr></thead>
  <tr>
    <td>&copy; 2022 OSCG Partners.&nbsp;All rights reserved.</td>
    <td>luss@oscg.io</td>
  </tr>
</table>

    </div>
  </div>
</div>
</div>
"""
, pOptFile)


def print_multilevel_head():
  print_file(
"""
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">

<style type="text/css">

/* ============ desktop view ============ */
@media all and (min-width: 992px) {

	.dropdown-menu li{
		position: relative;
	}
	.dropdown-menu .submenu{ 
		display: none;
		position: absolute;
		left:100%; top:-7px;
	}
	.dropdown-menu .submenu-left{
		right:100%; left:auto;
	}

	.dropdown-menu > li:hover{ background-color: #f1f1f1 }
	.dropdown-menu > li:hover > .submenu{
		display: block;
	}
}
/* ============ desktop view .end// ============ */

/* ============ small devices ============ */
@media (max-width: 991px) {

.dropdown-menu .dropdown-menu{
		margin-left:0.7rem; margin-right:0.7rem; margin-bottom: .5rem;
}

}
/* ============ small devices .end// ============ */

</style>


<script type="text/javascript">

	document.addEventListener("DOMContentLoaded", function(){

    	/////// Prevent closing from click inside dropdown
		document.querySelectorAll('.dropdown-menu').forEach(function(element){
			element.addEventListener('click', function (e) {
			  e.stopPropagation();
			});
		})

		// make it as accordion for smaller screens
		if (window.innerWidth < 992) {

			// close all inner dropdowns when parent is closed
			document.querySelectorAll('.navbar .dropdown').forEach(function(everydropdown){
				everydropdown.addEventListener('hidden.bs.dropdown', function () {
					// after dropdown is hidden, then find all submenus
					  this.querySelectorAll('.submenu').forEach(function(everysubmenu){
					  	// hide every submenu as well
					  	everysubmenu.style.display = 'none';
					  });
				})
			});
			
			document.querySelectorAll('.dropdown-menu a').forEach(function(element){
				element.addEventListener('click', function (e) {

				  	let nextEl = this.nextElementSibling;
				  	if(nextEl && nextEl.classList.contains('submenu')) {	
				  		// prevent opening link if link needs to open dropdown
				  		e.preventDefault();
				  		console.log(nextEl);
				  		if(nextEl.style.display == 'block'){
				  			nextEl.style.display = 'none';
				  		} else {
				  			nextEl.style.display = 'block';
				  		}

				  	}
				});
			})
		}
		// end if innerWidth

	}); 
	// DOMContentLoaded  end
</script>
"""
)


def print_multilevel_menu():
  print_file(
"""
<div class="container-fluid">

<!-- ======== MULTILEVEL_MENU ============= -->
<nav class="navbar navbar-expand-lg navbar-dark bg-dark">
 <div class="container-fluid">
        <a class="navbar-brand" href="index.html"><img src=img/oscg-bigsql-logo.png height=50 width=50 /></a>
  <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#main_nav"  aria-expanded="false" aria-label="Toggle navigation">
      <span class="navbar-toggler-icon"></span>
    </button>
  <div class="collapse navbar-collapse" id="main_nav">

	<ul class="navbar-nav">
		<li class="nav-item"><a class="nav-link" href="index.html">Home</a></li>
		<li class="nav-item dropdown">
			<a class="nav-link dropdown-toggle" href="#" data-bs-toggle="dropdown">  Platform  </a>
		    <ul class="dropdown-menu">
			  <li><a class="dropdown-item" href="postgres-hyper.html">HyperscalePG</a></li>
			  <li><a class="dropdown-item" href="postgres-core.html">Pure PostgreSQL&reg;</a></li>
			  <li><a class="dropdown-item" href="postgres-extensions.html">Postgres Extensions</a></li>
			  <li><a class="dropdown-item" href="postgres-apps.html">Postgres Applications</a></li>
			  <li><a class="dropdown-item" href="postgres-devs.html">Postgres DevOps</a></li>
			  <li><a class="dropdown-item" href="change-data-capture.html">Streaming & CDC</a></li>

			  <li><a class="dropdown-item disabled" href="postgres-fdws.html">Postgres FDWs</a></li>
			  <li><a class="dropdown-item disabled" href="sql-datastores.html">Other RDBMS</a></li>
			  <li><a class="dropdown-item disabled" href="purpose-built.html">Purpose-Built Datastores</a></li>
		    </ul>
		</li>
		<li class="nav-item"><a class="nav-link" href="downloads.html">Usage & Downloads</a></li>
		<li class="nav-item"><a class="nav-link" href="tutorial.html">Tutorial</a></li>
		<li class="nav-item"><a class="nav-link" href="about.html">About Us</a></li>
		<li class="nav-item"><a class="nav-link" href="contact_us.html">Contact Us</a></li>
		<li class="nav-item"><a class="nav-link" href="services.html">Services</a></li>
	</ul>

  </div> <!-- navbar-collapse.// -->
</nav>
"""
)
