- Connexion « avec son compte Payplug » (OAuth2 *authorization code* + PKCE, chemin
  `/oauth2/auth`) : hors périmètre. Ce flux demande un client enregistré par Payplug
  avec une adresse de rappel ; le module se limite au flux *client credentials* avec
  une clé OAuth2 créée dans le portail.
- Prévu pour une version 3 : paiement en un clic (carte enregistrée), paiement
  fractionné, paiement différé, Apple Pay et paiement intégré.
- Paiement en plusieurs fois (Oney 3x/4x) : non pris en charge. Il demande le panier
  détaillé (`payment_context`), une autorisation puis une capture, et des montants entre
  100 € et 3 000 €.
- Enregistrement de la carte (jetons) et paiements récurrents : non pris en charge.
- Capture différée (autorisation puis capture manuelle) : non prise en charge.
- Apple Pay et le paiement intégré (*Integrated Payment*, champs de carte dans la page
  Odoo) : non pris en charge ; seule la page hébergée est utilisée.
- Les marques de carte renvoyées par Payplug (`card.brand`) ne sont connues que par la
  documentation ; à vérifier avec de vraies transactions de test.
- Satispay, Scalapay et Wero n'ont pas de moyen de paiement correspondant dans Odoo 19 :
  ils ne sont pas proposés.

À vérifier avec de vraies clés de test Payplug (non vérifié, faute de compte) :

- le format exact des notifications (paiement et remboursement), en particulier la
  présence de `payment_id` dans celles des remboursements ;
- le code HTTP attendu par Payplug en réponse aux notifications, et s'il les renvoie
  après une erreur (le module répond 503 quand il ne peut pas relire le paiement) ;
- l'acceptation des champs `billing` / `shipping` envoyés (langue, téléphone, pays) ;
- l'abandon (`aborted`) d'un paiement quand le client clique sur *Annuler* ;
- les valeurs de `card.brand` (Visa, Mastercard, CB…) ;
- Bancontact, iDEAL et MyBank, qui demandent une activation sur le compte Payplug ;
- en OAuth2 : la valeur du *scope* des jetons de l'environnement Live (`live` est
  supposé ; une autre valeur est tolérée sur un fournisseur activé, le mode de chaque
  paiement restant vérifié).
