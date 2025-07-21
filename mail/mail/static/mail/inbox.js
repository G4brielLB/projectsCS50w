document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);
  document.querySelector('#compose-form').addEventListener('submit', send_email);

  // By default, load the inbox
  load_mailbox('inbox');
});

function send_email(event) {
  event.preventDefault();
  fetch('/emails', {
    method: 'POST',
    body: JSON.stringify({
      recipients: document.querySelector('#compose-recipients').value,
      subject: document.querySelector('#compose-subject').value,
      body: document.querySelector('#compose-body').value
    }),
    headers: {
      'Content-Type': 'application/json'
    }
  })
  .then(response => response.json())
  .then(() => load_mailbox('sent'))
}

function compose_email() {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';
}

function load_mailbox(mailbox) {
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  fetch(`/emails/${mailbox}`)
  .then(response => response.json())
  .then(emails => {
    emails.forEach(email => {
      // Create email div
      const emailDiv = document.createElement('div');
      emailDiv.className = 'email';
      emailDiv.style.border = '1px solid #ddd';
      emailDiv.style.padding = '10px';
      emailDiv.style.margin = '5px';
      emailDiv.style.cursor = 'pointer';
      emailDiv.style.display = 'flex';
      emailDiv.style.justifyContent = 'space-between';
      emailDiv.style.alignItems = 'center';
      emailDiv.style.backgroundColor = email.read ? 'lightgray' : 'white';

      // Create email content
      const emailContent = document.createElement('div');
      emailContent.innerHTML = `
        <strong>${mailbox === 'sent' ? 'To: ' + email.recipients : email.sender}</strong> - ${email.subject}
        <br>
        <small>${email.timestamp}</small>
      `;
      emailDiv.append(emailContent);

      const buttonContainer = document.createElement('div');

      // Archive, Unarchive and Reply buttons
      if (mailbox !== 'sent') { // Sent emails can't be archived, unarchived or replied
        // Archive and Unarchive buttons
        const archiveButton = document.createElement('button');
        archiveButton.innerHTML = email.archived ? '<i class="fa fa-folder-open"></i>' : '<i class="fa fa-folder"></i>';
        archiveButton.onclick = (event) => {
          event.stopPropagation();
          archive_email(email.id, email.archived);
        };
        buttonContainer.append(archiveButton);
        // Reply button
        const replyButton = document.createElement('button');
        replyButton.innerHTML = '<i class="fa fa-reply"></i>';
        replyButton.style.marginRight = '5px';
        replyButton.onclick = (event) => {
          event.stopPropagation();
          reply_email(email);
        };
        buttonContainer.append(replyButton);
      }

      emailDiv.append(buttonContainer);

      // Add click event to view email
      emailDiv.addEventListener('click', () => load_email(email.id));

      // Add to emails-view
      document.querySelector('#emails-view').append(emailDiv);
    });
  });
}

// Function to reply to email
function reply_email(email) {
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  document.querySelector('#compose-recipients').value = email.sender;
  document.querySelector('#compose-subject').value = email.subject.startsWith('Re:') ? email.subject : `Re: ${email.subject}`;
  document.querySelector('#compose-body').value = `\n\n\n### On ${email.timestamp}, ${email.sender} wrote:\n${email.body}`;
}

// Function to archive/unarchive email
function archive_email(email_id, is_archived) {
  fetch(`/emails/${email_id}`, {
    method: 'PUT',
    body: JSON.stringify({ archived: !is_archived })
  })
  .then(() => load_mailbox('inbox')); // Reload inbox after archiving/unarchiving
}

// Function to load email
function load_email(email_id) {

  let loggedUserEmail = '';

  fetch(`/emails/${email_id}`)
  .then(response => response.json())
  .then(email => {
    // Show email view and hide other views
    document.querySelector('#emails-view').style.display = 'block';
    document.querySelector('#compose-view').style.display = 'none';

    // Mark email as read
    fetch(`/emails/${email_id}`, {
      method: 'PUT',
      body: JSON.stringify({ read: true })
    });

    // Retrive logged email
    fetch('/get_user_email')
    .then(response => response.json())
    .then(data => {
      console.log(data);  
      loggedUserEmail = data.email;    
    })
    .then(() => {
      // Show email details
    const emailDiv = document.createElement('div');
    emailDiv.style.border = '1px solid #ddd';
    emailDiv.style.padding = '10px';
    emailDiv.style.margin = '5px';
    emailDiv.innerHTML = `
      <div style="display: flex; justify-content: space-between; align-items: center;">
      <div>
      <strong>From:</strong> ${email.sender}
      <br>
      <strong>To:</strong> ${email.recipients}
      <br>
      <strong>Subject:</strong> ${email.subject}
      <br>
      <strong>Timestamp:</strong> ${email.timestamp}
      </div>
      ${email.sender !== loggedUserEmail ? `
      <div>
      <button id="reply" class="btn btn-sm btn-outline-primary"><i class="fa fa-reply"></i></button>
      <button id="archive" class="btn btn-sm btn-outline-secondary"><i class="fa ${email.archived ? 'fa-folder-open' : 'fa-folder'}"></i></button>
      </div>
      ` : ''}
      </div>
      <hr>
      <div>${email.body}</div>
    `;

    document.querySelector('#emails-view').innerHTML = '';
    document.querySelector('#emails-view').append(emailDiv);
    
    // Add click event to archive/unarchive button
    document.querySelector('#archive').addEventListener('click', () => {
      archive_email(email.id, email.archived);
    });

    // Add click event to reply button
    document.querySelector('#reply').addEventListener('click', () => reply_email(email));
    })
    .catch(error => console.error('Erro ao obter e-mail:', error));



    
    
  });
}