const fs = require('fs');
const speakeasy = require('speakeasy');
const qrcode = require('qrcode');
const readline = require('readline-sync');

const SECRET_FILE = '2fa_secret.txt';

// Load or create a TOTP secret
function getOrCreateSecret() {
  if (fs.existsSync(SECRET_FILE)) {
    const secret = fs.readFileSync(SECRET_FILE, 'utf8').trim();
    console.log('[INFO] Loaded existing secret from file.');
    return secret;
  } else {
    const secret = speakeasy.generateSecret({ length: 32 });
    fs.writeFileSync(SECRET_FILE, secret.base32);
    console.log('[INFO] Generated and saved new secret.');
    generateQRCode(secret);
    return secret.base32;
  }
}

// Generate QR code for Google Authenticator
function generateQRCode(secret, filename = 'qrcode.png') {
  const otpauthURL = speakeasy.otpauthURL({
    secret: secret.base32 || secret, // if full secret object, extract base32
    label: 'user@example.com',
    issuer: 'MyApp',
    encoding: 'base32'
  });

  qrcode.toFile(filename, otpauthURL, (err) => {
    if (err) throw err;
    console.log(`[INFO] QR code saved as ${filename} (scan with Google Authenticator).`);
  });
}

// Verify OTP code entered by user
function verifyOTP(secret) {
  const token = readline.question('Enter the OTP from your authenticator app: ');
  const verified = speakeasy.totp.verify({
    secret,
    encoding: 'base32',
    token
  });

  const currentOTP = speakeasy.totp({
    secret,
    encoding: 'base32'
  });

  console.log('[DEBUG] Current OTP (for testing):', currentOTP);

  if (verified) {
    console.log('[SUCCESS] OTP is valid!');
  } else {
    console.log('[ERROR] Invalid OTP. Check the time sync and the code.');
  }
}

// Generate QR code for a new device
function addNewDevice(secret) {
  generateQRCode(secret, 'qrcode_new_device.png');
  console.log('[INFO] Use qrcode_new_device.png to add another device.');
}

// Main entry point
function main() {
  const args = process.argv.slice(2);
  const secret = getOrCreateSecret();

  if (args.includes('--new-device')) {
    addNewDevice(secret);
  } else {
    verifyOTP(secret);
  }
}

main();
