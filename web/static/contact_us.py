import oscg

oscg.PFILE="contact_us"
oscg.PAGE_TITLE="Contact Us"
oscg.PAGE_DESC = "Contact Us"

oscg.print_header()

oscg.print_file(
"""
<div class="container py-4">

  <!-- Bootstrap 5 starter form -->
  <form id="contactForm">

    <!-- Name input -->
    <div class="mb-3">
      <label class="form-label" for="name">Name</label>
      <input class="form-control" id="name" type="text" placeholder="Name" />
    </div>

    <!-- Email address input -->
    <div class="mb-3">
      <label class="form-label" for="emailAddress">Email Address</label>
      <input class="form-control" id="emailAddress" type="email" placeholder="Email Address" />
    </div>

    <!-- Message input -->
    <div class="mb-3">
      <label class="form-label" for="message">Message</label>
      <textarea class="form-control" id="message" type="text" placeholder="Message" style="height: 10rem;"></textarea>
    </div>

    <!-- Form submit button -->
    <div class="d-grid">
      <button class="btn btn-primary btn-lg" type="submit" disabled>Submit</button>
    </div>

  </form>

</div>
"""
)

oscg.print_footer()

