## 19.0.1.1.0 (2026-10-24)

- Authentification OAuth2 (*client credentials*) au choix, à côté de la clé API : jetons
  d'accès de 5 minutes gardés en mémoire et renouvelés automatiquement, nouvelle demande
  et renvoi unique de la requête si Payplug refuse le jeton, contrôle de
  l'environnement (Test ou Live) du jeton.

## 19.0.1.0.0 (2026-10-24)

- Première version : paiement par la page hébergée Payplug, notifications,
  remboursements totaux et partiels, paiement des factures.
