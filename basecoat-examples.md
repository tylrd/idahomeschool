
# card
<div class="card w-full">
  <header>
    <h2>Login to your account</h2>
    <p>Enter your details below to login to your account</p>
  </header>
  <section>
    <form class="form grid gap-6">
      <div class="grid gap-2">
        <label for="demo-card-form-email">Email</label>
        <input type="email" id="demo-card-form-email">
      </div>
      <div class="grid gap-2">
        <div class="flex items-center gap-2">
          <label for="demo-card-form-password">Password</label>
          <a href="#" class="ml-auto inline-block text-sm underline-offset-4 hover:underline">Forgot your password?</a>
        </div>
        <input type="password" id="demo-card-form-password">
      </div>
    </form>
  </section>
  <footer class="flex flex-col items-center gap-2">
    <button type="button" class="btn w-full">Login</button>
    <button type="button" class="btn-outline w-full">Login with Google</button>
    <p class="mt-4 text-center text-sm">Don't have an account? <a href="#" class="underline-offset-4 hover:underline">Sign up</a></p>
  </footer>
</div>

# checkbox
<label class="label gap-3">
  <input type="checkbox" class="input">
  Accept terms and conditions
</label>

# dialog
<button type="button" onclick="document.getElementById('demo-dialog-edit-profile').showModal()" class="btn-outline">Edit Profile</button>

<dialog id="demo-dialog-edit-profile" class="dialog w-full sm:max-w-[425px] max-h-[612px]" aria-labelledby="demo-dialog-edit-profile-title" aria-describedby="demo-dialog-edit-profile-description" onclick="if (event.target === this) this.close()">
  <div>
    <header>
      <h2 id="demo-dialog-edit-profile-title">Edit profile</h2>
      <p id="demo-dialog-edit-profile-description">Make changes to your profile here. Click save when you're done.</p>
    </header>

    <section>
      <form class="form grid gap-4">
        <div class="grid gap-3">
          <label for="demo-dialog-edit-profile-name">Name</label>
          <input type="text" value="Pedro Duarte" id="demo-dialog-edit-profile-name" autofocus />
        </div>
        <div class="grid gap-3">
          <label for="demo-dialog-edit-profile-username">Username</label>
          <input type="text" value="@peduarte" id="demo-dialog-edit-profile-username" />
        </div>
      </form>
    </section>

    <footer>
      <button class="btn-outline" onclick="this.closest('dialog').close()">Cancel</button>
      <button class="btn" onclick="this.closest('dialog').close()">Save changes</button>
    </footer>

    <button type="button" aria-label="Close dialog" onclick="this.closest('dialog').close()">
      <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-x-icon lucide-x">
        <path d="M18 6 6 18" />
        <path d="m6 6 12 12" />
      </svg>
    </button>
  </div>
</dialog>

# dropdown menu
<div id="demo-dropdown-menu" class="dropdown-menu">
  <button type="button" id="demo-dropdown-menu-trigger" aria-haspopup="menu" aria-controls="demo-dropdown-menu-menu" aria-expanded="false" class="btn-outline">Open</button>
  <div id="demo-dropdown-menu-popover" data-popover aria-hidden="true" class="min-w-56">
    <div role="menu" id="demo-dropdown-menu-menu" aria-labelledby="demo-dropdown-menu-trigger">
      <div role="group" aria-labelledby="account-options">
        <div role="heading" id="account-options">My Account</div>
        <div role="menuitem">
          Profile
          <span class="text-muted-foreground ml-auto text-xs tracking-widest">⇧⌘P</span>
        </div>
        <div role="menuitem">
          Billing
          <span class="text-muted-foreground ml-auto text-xs tracking-widest">⌘B</span>
        </div>
        <div role="menuitem">
          Settings
          <span class="text-muted-foreground ml-auto text-xs tracking-widest">⌘S</span>
        </div>
        <div role="menuitem">
          Keyboard shortcuts
          <span class="text-muted-foreground ml-auto text-xs tracking-widest">⌘K</span>
        </div>
      </div>
      <hr role="separator" />
      <div role="menuitem">GitHub</div>
      <div role="menuitem">Support</div>
      <div role="menuitem" aria-disabled="true">API</div>
      <hr role="separator" />
      <div role="menuitem">
        Logout
        <span class="text-muted-foreground ml-auto text-xs tracking-widest">⇧⌘P</span>
      </div>
    </div>
  </div>
</div>

# form
<form class="form grid gap-6">
  <div class="grid gap-2">
    <label for="demo-form-text">Username</label>
    <input type="text" id="demo-form-text" placeholder="hunvreus">
    <p class="text-muted-foreground text-sm">This is your public display name.</p>
  </div>

  <div class="grid gap-2">
    <label for="demo-form-select">Email</label>
    <select id="demo-form-select">
      <option value="bob@example.com">m@example.com</option>
      <option value="alice@example.com">m@google.com</option>
      <option value="john@example.com">m@support.com</option>
    </select>
    <p class="text-muted-foreground text-sm">You can manage email addresses in your email settings.</p>
  </div>

  <div class="grid gap-2">
    <label for="demo-form-textarea">Bio</label>
    <textarea id="demo-form-textarea" placeholder="I like to..." rows="3"></textarea>
    <p class="text-muted-foreground text-sm">You can @mention other users and organizations.</p>
  </div>

  <div class="grid gap-2">
    <label for="demo-form-date">Date of birth</label>
    <input type="date" id="demo-form-date">
    <p class="text-muted-foreground text-sm">Your date of birth is used to calculate your age.</p>
  </div>

  <div class="flex flex-col gap-3">
    <label for="demo-form-radio">Notify me about...</label>
    <fieldset id="demo-form-radio" class="grid gap-3">
      <label class="font-normal"><input type="radio" name="demo-form-radio" value="1" checked>All new messages</label>
      <label class="font-normal"><input type="radio" name="demo-form-radio" value="2">Direct messages and mentions</label>
      <label class="font-normal"><input type="radio" name="demo-form-radio" value="3" >Nothing</label>
    </fieldset>
  </div>

  <section class="grid gap-4">
    <h3 class="text-lg font-medium">Email Notifications</h3>
    <div class="gap-2 flex flex-row items-start justify-between rounded-lg border p-4 shadow-xs">
      <div class="flex flex-col gap-0.5">
        <label for="demo-form-switch" class="leading-normal">Marketing emails</label>
        <p class="text-muted-foreground text-sm">Receive emails about new products, features, and more.</p>
      </div>
      <input type="checkbox" id="demo-form-switch" role="switch">
    </div>
    <div class="gap-2 flex flex-row items-start justify-between rounded-lg border p-4 shadow-xs">
      <div class="flex flex-col gap-0.5 opacity-60">
        <label for="demo-form-switch-disabled" class="leading-normal">Security emails</label>
        <p class="text-muted-foreground text-sm">Receive emails about your account security.</p>
      </div>
      <input type="checkbox" id="demo-form-switch-disabled" role="switch" disabled>
    </div>
  </section>

  <button type="submit" class="btn">Submit</button>
</form>

# popover
<div id="demo-popover" class="popover">
  <button id="demo-popover-trigger" type="button" aria-expanded="false" aria-controls="demo-popover-popover" class="btn-outline">Open popover</button>
  <div id="demo-popover-popover" data-popover aria-hidden="true" class="w-80">
    <div class="grid gap-4">
      <header class="grid gap-1.5">
        <h4 class="leading-none font-medium">Dimensions</h4>
        <p class="text-muted-foreground text-sm">Set the dimensions for the layer.</p>
      </header>
      <form class="form grid gap-2">
        <div class="grid grid-cols-3 items-center gap-4">
          <label for="demo-popover-width">Width</label>
          <input type="text" id="demo-popover-width" value="100%" class="col-span-2 h-8" autofocus />
        </div>
        <div class="grid grid-cols-3 items-center gap-4">
          <label for="demo-popover-max-width">Max. width</label>
          <input type="text" id="demo-popover-max-width" value="300px" class="col-span-2 h-8" />
        </div>
        <div class="grid grid-cols-3 items-center gap-4">
          <label for="demo-popover-height">Height</label>
          <input type="text" id="demo-popover-height" value="25px" class="col-span-2 h-8" />
        </div>
        <div class="grid grid-cols-3 items-center gap-4">
          <label for="demo-popover-max-height">Max. height</label>
          <input type="text" id="demo-popover-max-height" value="none" class="col-span-2 h-8" />
        </div>
      </form>
    </div>
  </div>
</div>

# sidebar
<aside class="sidebar" data-side="left" aria-hidden="false">
  <nav aria-label="Sidebar navigation">
    <section class="scrollbar">
      <div role="group" aria-labelledby="group-label-content-1">
        <h3 id="group-label-content-1">Getting started</h3>

        <ul>
          <li>
            <a href="#">
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="m7 11 2-2-2-2" />
                <path d="M11 13h4" />
                <rect width="18" height="18" x="3" y="3" rx="2" ry="2" />
              </svg>
              <span>Playground</span>
            </a>
          </li>

          <li>
            <a href="#">
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M12 8V4H8" />
                <rect width="16" height="12" x="4" y="8" rx="2" />
                <path d="M2 14h2" />
                <path d="M20 14h2" />
                <path d="M15 13v2" />
                <path d="M9 13v2" />
              </svg>
              <span>Models</span>
            </a>
          </li>

          <li>
            <details id="submenu-content-1-3">
              <summary aria-controls="submenu-content-1-3-content">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z" />
                  <circle cx="12" cy="12" r="3" />
                </svg>
                Settings
              </summary>
              <ul id="submenu-content-1-3-content">
                <li>
                  <a href="#">
                    <span>General</span>
                  </a>
                </li>

                <li>
                  <a href="#">
                    <span>Team</span>
                  </a>
                </li>

                <li>
                  <a href="#">
                    <span>Billing</span>
                  </a>
                </li>

                <li>
                  <a href="#">
                    <span>Limits</span>
                  </a>
                </li>
              </ul>
            </details>
          </li>
        </ul>
      </div>
    </section>
  </nav>
</aside>

<main>
  <button type="button" onclick="document.dispatchEvent(new CustomEvent('basecoat:sidebar'))">Toggle sidebar</button>
  <h1>Content</h1>
</main>

# table
<div class="overflow-x-auto">
<table class="table">
  <caption>A list of your recent invoices.</caption>
  <thead>
    <tr>
      <th>Invoice</th>
      <th>Status</th>
      <th>Method</th>
      <th>Amount</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td class="font-medium">INV001</td>
      <td>Paid</td>
      <td>Credit Card</td>
      <td class="text-right">$250.00</td>
    </tr>
    <tr>
      <td class="font-medium">INV002</td>
      <td>Pending</td>
      <td>PayPal</td>
      <td class="text-right">$150.00</td>
    </tr>
    <tr>
      <td class="font-medium">INV003</td>
      <td>Unpaid</td>
      <td>Bank Transfer</td>
      <td class="text-right">$350.00</td>
    </tr>
    <tr>
      <td class="font-medium">INV004</td>
      <td>Paid</td>
      <td>Paypal</td>
      <td class="text-right">$450.00</td>
    </tr>
    <tr>
      <td class="font-medium">INV005</td>
      <td>Paid</td>
      <td>Credit Card</td>
      <td class="text-right">$550.00</td>
    </tr>
    <tr>
      <td class="font-medium">INV006</td>
      <td>Pending</td>
      <td>Bank Transfer</td>
      <td class="text-right">$200.00</td>
    </tr>
    <tr>
      <td class="font-medium">INV007</td>
      <td>Unpaid</td>
      <td>Credit Card</td>
      <td class="text-right">$300.00</td>
    </tr>
  </tbody>
  <tfoot>
    <tr>
      <td colspan="3">Total</td>
      <td class="text-right">$2,500.00</td>
    </tr>
  </tfoot>
</table>
</div>

# tabs
<div class="tabs w-full" id="demo-tabs-with-panels">
  <nav role="tablist" aria-orientation="horizontal" class="w-full">
    <button type="button" role="tab" id="demo-tabs-with-panels-tab-1" aria-controls="demo-tabs-with-panels-panel-1" aria-selected="true" tabindex="0">Account</button>

    <button type="button" role="tab" id="demo-tabs-with-panels-tab-2" aria-controls="demo-tabs-with-panels-panel-2" aria-selected="false" tabindex="0">Password</button>
  </nav>

  <div role="tabpanel" id="demo-tabs-with-panels-panel-1" aria-labelledby="demo-tabs-with-panels-tab-1" tabindex="-1" aria-selected="true">
    <div class="card">
      <header>
        <h2>Account</h2>
        <p>Make changes to your account here. Click save when you're done.</p>
      </header>
      <section>
        <form class="form grid gap-6">
          <div class="grid gap-3">
            <label for="demo-tabs-account-name">Name</label>
            <input type="text" id="demo-tabs-account-name" value="Pedro Duarte" />
          </div>
          <div class="grid gap-3">
            <label for="demo-tabs-account-username">Username</label>
            <input type="text" id="demo-tabs-account-username" value="@peduarte" />
          </div>
        </form>
      </section>
      <footer>
        <button type="button" class="btn">Save changes</button>
      </footer>
    </div>
  </div>

  <div role="tabpanel" id="demo-tabs-with-panels-panel-2" aria-labelledby="demo-tabs-with-panels-tab-2" tabindex="-1" aria-selected="false" hidden>
    <div class="card">
      <header>
        <h2>Password</h2>
        <p>Change your password here. After saving, you'll be logged out.</p>
      </header>
      <section>
        <form class="form grid gap-6">
          <div class="grid gap-3">
            <label for="demo-tabs-password-current">Current password</label>
            <input type="password" id="demo-tabs-password-current" />
          </div>
          <div class="grid gap-3">
            <label for="demo-tabs-password-new">New password</label>
            <input type="password" id="demo-tabs-password-new" />
          </div>
        </form>
      </section>
      <footer>
        <button type="button" class="btn">Save Password</button>
      </footer>
    </div>
  </div>
</div>

# theme switcher
<button
  type="button"
  aria-label="Toggle dark mode"
  data-tooltip="Toggle dark mode"
  data-side="bottom"
  onclick="document.dispatchEvent(new CustomEvent('basecoat:theme'))"
  class="btn-icon-outline size-8"
>
  <span class="hidden dark:block"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4" /><path d="M12 2v2" /><path d="M12 20v2" /><path d="m4.93 4.93 1.41 1.41" /><path d="m17.66 17.66 1.41 1.41" /><path d="M2 12h2" /><path d="M20 12h2" /><path d="m6.34 17.66-1.41 1.41" /><path d="m19.07 4.93-1.41 1.41" /></svg></span>
  <span class="block dark:hidden"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z" /></svg></span>
</button>