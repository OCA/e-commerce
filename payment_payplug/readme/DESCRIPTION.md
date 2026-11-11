Ce module ajoute [Payplug](https://www.payplug.com/) comme fournisseur de paiement au
cadre de paiement d'Odoo (module `payment`).

Le client est redirigé vers la page de paiement hébergée par Payplug, puis revient sur
Odoo. Le module gère :

- le paiement en ligne sur le site web (panier et validation de commande) ;
- le paiement des factures depuis le portail client et par lien de paiement ;
- les notifications serveur de Payplug (paiements et remboursements) ;
- les remboursements totaux et partiels depuis Odoo, et ceux faits depuis le portail
  Payplug ;
- les annulations, les échecs et les paiements expirés.

Payplug n'accepte que l'euro : le fournisseur n'est proposé que pour les paiements en EUR.

Le module appelle directement l'API REST de Payplug avec `requests` ; il ne demande
aucune bibliothèque Python supplémentaire.

**Avertissement :** ce module est un développement indépendant. Il n'est ni affilié à
Payplug, ni approuvé par Payplug. « Payplug » est une marque de son propriétaire.
