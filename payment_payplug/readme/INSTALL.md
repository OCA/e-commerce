Le module dépend des modules standard `payment` et `account_payment` (installés avec la
Facturation ou le site e-commerce). Il ne demande aucune bibliothèque Python
supplémentaire.

1. Placez le dossier `payment_payplug` dans un chemin d'extensions (`addons_path`)
   d'Odoo 19, ou installez le paquet Python construit avec `pyproject.toml`.
2. Redémarrez Odoo, mettez à jour la liste des applications, puis installez
   *Payment Provider: Payplug*.

Le fournisseur *Payplug* est créé désactivé, pour chaque société.

À la désinstallation, comme pour les fournisseurs standard, Odoo refuse de continuer si
des paiements comptables ont été faits avec Payplug. Un fournisseur qui n'a que des
transactions sans paiement est conservé (désactivé, sans code) pour garder ces
transactions lisibles ; sinon il est supprimé.
