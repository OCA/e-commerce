* Computing this requires 1 or 2 extra calls to ``taxes.compute_all()`` per
  product. This could be expensive in terms of performance, but the truth is
  that it is also not very optimized upstream in Odoo. Maybe optimize this part
  in Odoo and in this module? Or maybe apply some hack to avoid recomputing
  this? Maybe cache calls to that method? Is it really a problem in the
  Real World®?
