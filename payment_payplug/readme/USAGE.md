**Paiement sur le site web ou depuis le portail**

Le client choisit *Carte* (ou un autre moyen activé), est redirigé vers la page Payplug,
paie, puis revient sur la page d'état du paiement d'Odoo. La commande ou la facture est
confirmée dès qu'Odoo a relu le paiement auprès de Payplug, soit au retour du client,
soit à la réception de la notification.

Si le client clique sur *Annuler* sur la page Payplug, le paiement est abandonné chez
Payplug et la transaction passe à l'état *Annulée*. Un paiement refusé passe à l'état
*Erreur* avec le motif donné par Payplug ; un paiement jamais terminé est annulé quand
Payplug signale son expiration (environ 15 minutes).

**Remboursement**

Depuis le paiement (*Comptabilité > Clients > Paiements*), ou depuis la facture via son
paiement, cliquez sur *Rembourser* et indiquez le montant (total ou partiel). Odoo
demande le remboursement à Payplug, crée une transaction de remboursement liée à la
transaction d'origine, puis le paiement comptable négatif correspondant.

Un remboursement fait directement dans le portail Payplug est aussi enregistré dans
Odoo, à la réception de sa notification.

Payplug n'accepte pas de remboursement inférieur à 0,10 €.

**Vérifier une transaction**

Sur une transaction Payplug en attente ou en erreur, le bouton *Vérifier le statut sur
Payplug* relit le paiement auprès de Payplug et met la transaction à jour (utile si une
notification n'a pas pu arriver).
