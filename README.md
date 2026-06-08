# Hackstreet Goldberg
An modular multi-station _Turing Goldberg_ machine.

## Project Structure
The `components` folder contains all the API endpoints and business logic.
The currently supported operations are:
* Speech-to-text webpages
* Sending e-mails via `google` and `selenium`
* Receiving e-mails via `google` and `selenium`
* Encoding strings to our proprietary HGAEF (_Hackstreet Goldberg Audiowave Encoding Format) format and broadcasting it with `desmos`
* Decoding HGAE using speakers
* Converting strings to QR-codes
* Displaying QR-codes in `Minecraft Java` and a screenshot of it

## Example
`components/pileline` has an example pipeline that translates Japanese speech to english text.
* `Station 1` converts japanese speech to english text and applies a Caesar cipher to it. It then sends it by e-mail to `Station 2`.
* `Station 2` receives the e-mail and broadcasts the corresponding HGAEF to `Station 3`
* `Station 3` decode the audio, undos the cipher and converts the string to a QR-code. It then builds the QR-code in `Minecraft`. It takes a screenshot of the QR-code, and e-mails it back `Station 1`.
* `Station 1` receives the screenshot by e-mail and opens up a webapp displaying the final result.
