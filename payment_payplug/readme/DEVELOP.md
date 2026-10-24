Les tests automatiques (`--test-tags /payment_payplug`) n'appellent jamais l'API Payplug :
ils démarrent un faux serveur Payplug local (`tests/fake_payplug.py`) et y font pointer
le module par le paramètre système `payment_payplug.api_base_url`.

Le même faux serveur sert aux essais manuels de bout en bout, avec une page de paiement
factice (boutons *Payer*, *Refuser*, *Annuler*) et l'envoi des notifications :

``` shell
python3 payment_payplug/tests/fake_payplug.py --host 127.0.0.1 --port 8765
```

Sur une base de test, créez alors le paramètre système `payment_payplug.api_base_url`
avec la valeur `http://127.0.0.1:8765/v1/`, et saisissez une clé quelconque commençant
par `sk_test_`. `POST /_control/refund/<id du paiement>` (corps `{"amount": 1000}`)
simule un remboursement fait depuis le portail Payplug.

Pour essayer la méthode OAuth2, le faux serveur répond aussi sur `POST /oauth2/token`
(authentification *Basic*, `grant_type=client_credentials`, audience
`https://www.payplug.com`) avec deux clients factices : `fake_client_test` /
`fake_client_secret_test` (jetons de test) et `fake_client_live` /
`fake_client_secret_live` (jetons Live). L'adresse du point de jeton se déduit de
`payment_payplug.api_base_url` ; il n'y a rien d'autre à régler.
