# Nimbus Platform: Resource Quotas

## Default quota
Every team namespace starts with a quota of 4 CPU cores and 8 GiB of memory, shared by all pods in that namespace.

## Requesting more resources
To get more CPU or memory, raise a quota request in the Nimbus portal with your current usage graph and the reason. The platform team reviews requests within 2 business days. The maximum quota for one namespace is 32 CPU cores and 64 GiB of memory.

## Out of memory errors
If pods are killed with OOMKilled, first check the memory limit in your deployment. Raising the pod limit does not help when the namespace quota is already used up; in that case request a quota increase.
