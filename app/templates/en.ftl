welcome-one = 👋 <b>Hello, { $user_firstname }!</b>

              The bot setup pipeline will take 3-5 minutes.
              First, read this <a href="https://blog.karych.ru/lesst">article</a>. If you still have questions, ask them in @InnerBotsSupport.

welcome-two = Let's start! Press <b>Connect new Email</b> button
cancel = ✖️ Cancel action!
menu-connect_email = ➕ Connect new Email
menu-emails = 📮 My Emails
menu-subscription = 💟 Subscription
auth-choose_email_service = <b>Step 1.</b>
                            Choose your Email-service:
auth-enter_email = 🏠 Email-service: <code>{ $email_service }</code>

                   <b>Enter 📮 Email-address:</b>
auth-incorrect_email = 🏠 Email-service: <code>{ $email_service }</code>

                       <b>Incorrect Email: wrong format or already added. Try again:</b>
auth-set_imap_params-yandex = 🏠 Email-service: <code>{ $email_service }</code>
                              📮 Email: <code>{ $email }</code>

                              <b>1.</b> Open <a href="https://mail.yandex.ru/?dpda=yes#setup/client">this menu</a> and activate 2 checkboxes:
auth-set_imap_params-gmail = 🏠 Email-service: <code>{ $email_service }</code>
                             📮 Email: <code>{ $email }</code>

                             <b>1.</b> Open <a href="https://mail.google.com/mail/u/0/#settings/fwdandpop">this menu</a> and activate checkboxes. <b>Do not forget tap on button "Сохранить изменения"</b>
auth-set_imap_params-mail_ru = 🏠 Email-service: <code>{ $email_service }</code>
                               📮 Email: <code>{ $email }</code>

                               <b>1.</b> Compare your settings with checkboxes on the picture:
auth-enter_password = <b>2.</b> Generate access key in <a href="{ $tutorial_url }">this menu</a>, then enter:
auth-connection_refused = 🏠 <b>Email-service:</b> <code>{ $email_service }</code>
                          📮 <b>Email:</b> <code>{ $email }</code>
                          🔑 <b>Auth key:</b> <span class="tg-spoiler">{ $password }</span>

                          ❌ Email connection refused! How to solve:
                          <b>1.</b> Check pair email - auth key (generate it here: { $tutorial_url }).
                          <b>2.</b> Check if IMAP ({ $imap_tutorial_url }) is enabled, like on the picture:
auth-connection_success = 🏠 <b>Email-service:</b> <code>{ $email_service }</code>
                          📮 <b>Email:</b> <code>{ $email }</code>
                          🔑 <b>Auth key:</b> <span class="tg-spoiler">{ $password }</span>

                          ✅ <b>Email has been successfully connected to bot!</b>
auth-create_group = <b>Step 2.</b>

                    <b>1.</b> Create private group and enable "Topics" in settings, like on picture
auth-add_to_chat = <b>2.</b> Tap on button and add bot to created group.
                   Give access rights, marked on picture.

                   <i>(You can give all rights, if you want)</i>
auth-emails_count_limit_exceeded = You can't add new Email, because in your tariff, you can connect only { $max_emails_count } Emails.

                                   — To add new, you should delete one of the added yet. Press "My Emails" button
                                   — If you want increase limits, press "Subscription" button
auth-no_added_emails = You don't have any connected Email boxes
forum-general_topic_name = Service messages
forum-email_not_added = Before adding a bot to a group, you need to connect your email to the bot. Go to the @mail_inbot PM and click /start
forum-group_added = ✔️ The group has been added successfully. Emails will be uploaded to the sidebar within a few minutes. The more emails you have, the longer the process will take.

                    <i>You can exit the chat, the download will not be interrupted.</i>
forum-no_permissions = Bot added without access rights.
                       Provide access rights, like on the picture. Bot will work automatically
forum-not_forum = Bot added, but "Topics" are disabled. How to fix:
                  1) Remove bot from this group
                  2) Enable "Topics" in group
                  3) Add bot to group again
forum-bot_removed = The bot has been removed from forum. Add the bot again and provide admin rights
forum-topic_send_email = Send Email
button-remove_email = Remove Email
button-back_to_email_services = 🔙 Back to Email-services
button-back_to_email_address = 🔙 Back to Email
button-add_to_chat = Add to chat
email_form = From: { $from_address }
             To: { $to_address }
             Subject: { $subject }

             { $plain_text_with_entities }
