<?php
declare(strict_types=1);

/**
 * Kontaktformular-Endpunkt für ERNST HAUS & GARTEN
 * Läuft auf IONOS Webhosting Standard (PHP 8.2+).
 * Form-Daten validieren, Spam filtern, Mail an Inhaber senden.
 */

const RECIPIENT       = 'info@ernst-hausgarten.de';
const FROM_ADDRESS    = 'info@ernst-hausgarten.de';
const SITE_NAME       = 'ERNST HAUS & GARTEN';
const SUCCESS_URL     = '/kontakt/danke';
const MAX_MESSAGE_LEN = 5000;
const MIN_FORM_SECONDS = 2;

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    header('Allow: POST');
    exit('Method Not Allowed');
}

function input(string $key): string {
    return trim((string)($_POST[$key] ?? ''));
}

function strip_lines(string $s): string {
    return preg_replace('/[\r\n]+/', ' ', $s) ?? '';
}

$name      = input('name');
$email     = input('email');
$telefon   = input('telefon');
$ort       = input('ort');
$leistung  = input('leistung');
$nachricht = input('nachricht');
$consent   = isset($_POST['datenschutz']);
$honeypot  = input('website');
$ts        = (int)input('ts');

// Honeypot: Bots füllen verstecktes Feld → stille Annahme, kein Versand
if ($honeypot !== '') {
    header('Location: ' . SUCCESS_URL, true, 303);
    exit;
}

// Timing: Formular zu schnell abgesendet → Bot
if ($ts > 0 && (time() - $ts) < MIN_FORM_SECONDS) {
    header('Location: ' . SUCCESS_URL, true, 303);
    exit;
}

$errors = [];
if ($name === '')                                               $errors[] = 'Bitte Namen angeben.';
if ($email === '' || !filter_var($email, FILTER_VALIDATE_EMAIL)) $errors[] = 'Bitte gültige E-Mail-Adresse angeben.';
if ($nachricht === '')                                          $errors[] = 'Bitte Nachricht ausfüllen.';
if (strlen($nachricht) > MAX_MESSAGE_LEN)                       $errors[] = 'Nachricht ist zu lang (max. 5000 Zeichen).';
if (!$consent)                                                  $errors[] = 'Bitte der Datenschutzerklärung zustimmen.';

if ($errors) {
    show_error_page(400, 'Anfrage unvollständig', $errors);
    exit;
}

$subject_raw = '[Website] Neue Anfrage von ' . strip_lines($name);
$subject = '=?UTF-8?B?' . base64_encode($subject_raw) . '?=';

$lines = [
    'Neue Anfrage über das Kontaktformular',
    str_repeat('=', 40),
    '',
    'Name:      ' . $name,
    'E-Mail:    ' . $email,
];
if ($telefon !== '')  $lines[] = 'Telefon:   ' . $telefon;
if ($ort !== '')      $lines[] = 'Ort:       ' . $ort;
if ($leistung !== '') $lines[] = 'Leistung:  ' . $leistung;
$lines[] = '';
$lines[] = '--- Nachricht ---';
$lines[] = $nachricht;
$lines[] = '';
$lines[] = '--- Technisch ---';
$lines[] = 'Zeit:  ' . date('Y-m-d H:i:s');
$lines[] = 'IP:    ' . ($_SERVER['REMOTE_ADDR'] ?? '?');
$lines[] = 'Agent: ' . substr((string)($_SERVER['HTTP_USER_AGENT'] ?? '?'), 0, 200);
$body = implode("\n", $lines);

$from_name = SITE_NAME;
$headers  = 'From: ' . $from_name . ' <' . FROM_ADDRESS . ">\r\n";
$headers .= 'Reply-To: ' . strip_lines($name) . ' <' . strip_lines($email) . ">\r\n";
$headers .= "MIME-Version: 1.0\r\n";
$headers .= "Content-Type: text/plain; charset=utf-8\r\n";
$headers .= "Content-Transfer-Encoding: 8bit\r\n";
$headers .= 'X-Mailer: PHP/' . phpversion();

$sent = @mail(RECIPIENT, $subject, $body, $headers, '-f' . FROM_ADDRESS);

if (!$sent) {
    show_error_page(500, 'Versand fehlgeschlagen', [
        'Ihre Anfrage konnte aus technischen Gründen nicht gesendet werden.',
        'Bitte schreiben Sie uns direkt per WhatsApp oder E-Mail – Kontaktdaten siehe unten.',
    ]);
    exit;
}

header('Location: ' . SUCCESS_URL, true, 303);
exit;

function show_error_page(int $status, string $title, array $messages): void {
    http_response_code($status);
    header('Content-Type: text/html; charset=utf-8');
    $items = '';
    foreach ($messages as $m) {
        $items .= '<li>' . htmlspecialchars($m, ENT_QUOTES, 'UTF-8') . '</li>';
    }
    $titleEsc = htmlspecialchars($title, ENT_QUOTES, 'UTF-8');
    echo <<<HTML
<!doctype html>
<html lang="de">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>$titleEsc – ERNST HAUS & GARTEN</title>
  <style>
    body { font-family: system-ui, -apple-system, sans-serif; max-width: 640px; margin: 3rem auto; padding: 0 1.25rem; color: #292521; line-height: 1.55; }
    h1 { color: #3d6330; font-size: 1.75rem; margin-bottom: .5rem; }
    ul { background: #fafaf7; border: 1px solid #e5e3dd; border-radius: .75rem; padding: 1rem 1rem 1rem 2.25rem; }
    .actions { margin-top: 2rem; display: flex; flex-wrap: wrap; gap: .75rem; }
    .btn { display: inline-flex; align-items: center; gap: .5rem; padding: .75rem 1.25rem; border-radius: .625rem; text-decoration: none; font-weight: 600; font-size: .95rem; }
    .btn-primary { background: #6aab54; color: #fff; }
    .btn-wa { background: #25D366; color: #fff; }
    .btn-secondary { background: #f0efea; color: #292521; border: 1px solid #e5e3dd; }
    .contact { margin-top: 2rem; padding: 1rem 1.25rem; background: #fafaf7; border-radius: .75rem; font-size: .9rem; color: #6b6660; }
    .contact a { color: #3d6330; }
  </style>
</head>
<body>
  <h1>$titleEsc</h1>
  <ul>$items</ul>
  <div class="actions">
    <a href="/kontakt" class="btn btn-primary">Zurück zum Formular</a>
    <a href="https://wa.me/4917661331466" class="btn btn-wa">WhatsApp schreiben</a>
    <a href="tel:+4917661331466" class="btn btn-secondary">Anrufen</a>
  </div>
  <div class="contact">
    Direktkontakt: <a href="mailto:info@ernst-hausgarten.de">info@ernst-hausgarten.de</a> &middot; +49 176 61331466
  </div>
</body>
</html>
HTML;
}
