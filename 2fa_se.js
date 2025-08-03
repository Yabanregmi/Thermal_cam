const express = require('express');
const speakeasy = require('speakeasy');
const qrcode = require('qrcode');
const fs = require('fs');
const bodyParser = require('body-parser');
const path = require('path');

const app = express();
app.set('view engine', 'ejs');
app.use(bodyParser.urlencoded({ extended: false }));
app.use(express.static('public'));

const USERS_DB = './users.json';

function loadUser(email) {
  const data = JSON.parse(fs.readFileSync(USERS_DB));
  return data[email];
}

function saveUser(user) {
  const data = JSON.parse(fs.readFileSync(USERS_DB));
  data[user.email] = user;
  fs.writeFileSync(USERS_DB, JSON.stringify(data, null, 2));
}

// --- 2FA SETUP ---
app.get('/setup-2fa', (req, res) => {
  const user = loadUser('user@example.com');

  const secret = speakeasy.generateSecret({
    name: `MyApp (${user.email})`
  });

  user.otpSecret = secret.base32;
  saveUser(user);

  const otpauth = speakeasy.otpauthURL({
    secret: secret.base32,
    label: user.email,
    issuer: 'MyApp'
  });

  qrcode.toDataURL(otpauth, (err, dataUrl) => {
    res.render('setup', { qr: dataUrl });
  });
});

app.post('/verify-2fa-setup', (req, res) => {
  const user = loadUser('user@example.com');
  const verified = speakeasy.totp.verify({
    secret: user.otpSecret,
    encoding: 'base32',
    token: req.body.otp
  });

  if (verified) {
    user.is2faEnabled = true;
    saveUser(user);
    res.send(' 2FA wurde erfolgreich aktiviert.');
  } else {
    res.send(' Ungültiger Code. Bitte erneut versuchen.');
  }
});

// --- 2FA LOGIN ---
app.get('/login', (req, res) => {
  const user = loadUser('user@example.com');
  if (!user.is2faEnabled) return res.redirect('/setup-2fa');
  res.render('verify');
});

app.post('/login', (req, res) => {
  const user = loadUser('user@example.com');
  const verified = speakeasy.totp.verify({
    secret: user.otpSecret,
    encoding: 'base32',
    token: req.body.otp,
    window: 1
  });

  if (verified) {
    res.send(' Login erfolgreich mit 2FA!');
  } else {
    res.send(' Falscher 2FA-Code.');
  }
});

app.listen(3000, () => console.log('2FA App läuft auf http://localhost:3000'));
