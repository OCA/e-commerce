**Clés Payplug**

Le module accepte deux méthodes d'authentification, au choix dans le champ
*Authentification* de l'onglet *Identifiants* :

- **Clé API** (par défaut) : la clé secrète du compte est envoyée à chaque requête ;
- **OAuth2** : Odoo échange un identifiant client (*client ID*) et un secret client
  (*client secret*) contre des jetons d'accès valables 5 minutes, demandés et renouvelés
  automatiquement. Le secret ne circule que vers le serveur d'autorisation de Payplug.

1. Dans le portail Payplug, à la rubrique des clés d'API, générez une clé en
   environnement **Test** et, plus tard, une clé en environnement **Live** :
   - pour la méthode *Clé API*, une clé de type **API Key** (clé secrète). Les clés
     actuelles sont des jetons JWT (`eyJ...`) ; les anciennes clés `sk_test_...` et
     `sk_live_...` sont aussi acceptées ;
   - pour la méthode *OAuth2*, une clé de type **OAuth2**. Le portail affiche son
     *client ID* et son *client secret* ; notez le secret aussitôt, il n'est montré
     qu'une fois.

   La clé publique n'est pas utilisée : le module ne passe que par la page de paiement
   hébergée.
2. Dans Odoo, ouvrez *Facturation (ou Comptabilité) > Configuration > Fournisseurs de
   paiement* et choisissez **Payplug**.
3. Dans l'onglet *Identifiants*, choisissez la méthode d'authentification, puis collez
   la clé secrète (*Clé API*) ou le *client ID* et le *client secret* (*OAuth2*). Seuls
   les administrateurs (groupe *Paramètres*) peuvent les lire ou les modifier.
4. Réglez l'état :
   - **Mode test** avec une clé de l'environnement Test : aucun débit réel ;
   - **Activé** avec une clé de l'environnement Live : paiements réels.

   Pour une ancienne clé `sk_...`, Odoo refuse une clé de production en mode test et
   une clé de test sur un fournisseur activé. Pour une clé JWT, l'accord entre le mode
   et la clé est vérifié à chaque paiement : un paiement dont le mode ne correspond
   pas est refusé. En OAuth2, l'environnement du jeton (*scope* `test`) est en plus
   vérifié à chaque requête : en mode test, seul un jeton de l'environnement Test est
   accepté ; sur un fournisseur activé, un jeton de test est refusé.

   Pour passer de Test à Live en OAuth2, remplacez le *client ID* et le *client secret*
   par ceux de la clé Live en même temps que vous activez le fournisseur.
5. Dans l'onglet *Configuration*, vérifiez le journal de paiement et les moyens de
   paiement. Par défaut, seul *Carte* (CB, Visa, Mastercard) est activé. Bancontact,
   iDEAL et MyBank sont proposés, mais ne les activez qu'après les avoir fait ouvrir sur
   votre compte Payplug.
6. Publiez le fournisseur pour qu'il apparaisse sur le site web.

**Adresse de notification (webhook)**

Le module donne à Payplug, pour chaque paiement, l'adresse
`https://<votre-domaine>/payment/payplug/webhook`. Il n'y a rien à saisir dans le portail
Payplug, mais cette adresse doit être joignable depuis Internet en HTTPS :

- ne la protégez pas par une authentification, un filtrage IP ou une règle de pare-feu
  (WAF, fail2ban, Cloudflare…) qui bloquerait les requêtes POST de Payplug ;
- vérifiez le paramètre système `web.base.url` (ou le domaine du site web) : c'est lui
  qui sert à construire les adresses de retour et de notification.

Les retours du client passent par `/payment/payplug/return` et `/payment/payplug/cancel`.

**Jetons d'accès OAuth2**

Un jeton dure 5 minutes ; Odoo le garde en mémoire et en demande un nouveau une minute
avant son expiration. Les jetons ne sont jamais écrits en base ni dans les journaux ;
chaque processus (worker) d'Odoo demande les siens. Si Payplug refuse un jeton (HTTP
401), Odoo l'oublie, en demande un autre et renvoie la requête une seule fois.
Après une modification des identifiants, chaque processus demande un nouveau jeton dès
sa requête suivante ; après un changement d'état, le jeton en mémoire est de nouveau
confronté au mode du fournisseur.

**Paramètres système réservés aux tests**

Ils ne servent qu'à pointer vers un faux serveur de test ; ne les créez pas en
production.

- `payment_payplug.api_base_url` remplace l'adresse de l'API Payplug
  (`https://api.payplug.com/v1/` par défaut) ;
- `payment_payplug.token_url` remplace l'adresse du point d'obtention des jetons OAuth2
  (par défaut `/oauth2/token` sur l'hôte de l'API, soit
  `https://api.payplug.com/oauth2/token`) ;
- `payment_payplug.token_audience` remplace l'audience demandée pour les jetons
  (`https://www.payplug.com` par défaut).
