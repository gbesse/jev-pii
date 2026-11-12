import random

def sample_strata(stratum_sizes,budget,seed=7):
 error='Échantillonnage stratifié invalide / Invalid stratified sampling / Muestreo estratificado inválido'
 if not isinstance(stratum_sizes,dict)or len(stratum_sizes)>1000 or type(budget)is not int or not 0<=budget<=100000 or type(seed)is not int:raise ValueError(error)
 if any(not isinstance(k,str)or not k or type(v)is not int or not 0<=v<=10000000 for k,v in stratum_sizes.items()):raise ValueError(error)
 sizes=dict(sorted(stratum_sizes.items()));positive=[k for k,n in sizes.items()if n];target=min(budget,sum(sizes.values()));allocation={k:1 if k in positive and target>=len(positive)else 0 for k in sizes};remaining=target-sum(allocation.values());capacity={k:sizes[k]-allocation[k]for k in sizes};total=sum(capacity.values())
 if total:
  quotas={k:remaining*capacity[k]/total for k in sizes};floors={k:int(q)for k,q in quotas.items()}
  for k,v in floors.items():allocation[k]+=v
  left=remaining-sum(floors.values())
  for k in sorted(sizes,key=lambda k:(-(quotas[k]-floors[k]),k))[:left]:allocation[k]+=1
 rng=random.Random(seed);selected={k:sorted(rng.sample(range(sizes[k]),allocation[k]))for k in sizes}
 return {'allocation':allocation,'selected_indices':selected,'uninspected_nonempty_strata':[k for k in positive if allocation[k]==0],'sampled':target,'seed':seed,'pii_absence_proven':False,'values_exported':False}
