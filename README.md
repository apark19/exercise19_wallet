# exercise19_wallet

<p>Usage: python wallet.py -c config -t token_type -i index -a amount</br>

This script is designed to leverage the hd-derive-wallet tool. </br>
This script will boot, generate a set of 10 keys for tokens, BTC-TEST and ETH-TEST. </br>
When using this script for BTC-TEST, a btc-test private key must be in the config and provided as an option, -c. </br>
The script will then take this private key, load the account, generate a new set of keys, then send the provided amount (also as an option, -a) to one of the addresses that were generated. </br></br>

ETH-TEST still in production...</br>
Current Status: The provided amount will be sent from one account to another on the Ganache private network. </br>

</p>



