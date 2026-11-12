.. Magnum After Heat: Pluggable Cluster API Drivers and the Road to
   Self-Managing Kubernetes

   OpenInfra Day US 2026 -- 20 minute talk.

   Run with:   presentty magnum-after-heat.rst
   Presenter:  presentty-console magnum-after-heat.rst
   Validate:   presentty --warnings magnum-after-heat.rst

   Speaker notes live in ".. container:: handout" blocks and are shown
   in presentty-console.

.. transition:: dissolve
   :duration: 0.4

Title
=====
.. hidetitle::
.. container:: handout

   ~0:30. Introduce yourself. One-sentence pitch: Magnum no longer
   depends on Heat; drivers are pluggable and Cluster API based, and
   we are adding an in-tree reference driver that builds its own
   management cluster.

::

    __  __
   |  \/  | __ _  __ _ _ __  _   _ _ __ ___
   | |\/| |/ _` |/ _` | '_ \| | | | '_ ` _ \
   | |  | | (_| | (_| | | | | |_| | | | | | |
   |_|  |_|\__,_|\__, |_| |_|\__,_|_| |_| |_|
                 |___/          after Heat


*Pluggable Cluster API Drivers and the Road to Self-Managing Kubernetes*

Michal Nasiadka -- StackHPC

OpenInfra Day US 2026

Agenda
======
.. container:: handout

   ~0:20. Four sections, roughly 5 minutes each.

.. container:: progressive

   * Why the Heat driver had to go
   * Driver pluggability: what it means for operators today
   * The missing piece: management clusters
   * k8s_kubeadm_v1: bootstrap, pivot, self-manage
   * What's next for Magnum

Magnum in one slide
===================
.. container:: handout

   ~1:00. Set the scene for people who have not touched Magnum.
   The key point: Magnum core is an API + conductor; the driver does
   the real work. That split is what made it possible to swap Heat out.

::

    openstack coe cluster create ...
                 |
                 v
   +----------------------+     +-------------------------+
   |  magnum-api          |     |  Cluster Template       |
   |  (REST, RBAC, quota) |<--->|  image, flavors, labels |
   +----------+-----------+     |  driver                 |
              | RPC             +-------------------------+
              v
   +----------------------+
   |  magnum-conductor    |
   |    +--------------+  |
   |    |   driver     |--+----> OpenStack / Kubernetes APIs
   |    +--------------+  |
   +----------------------+

The Heat era
============
.. container:: handout

   ~1:00. Explain how the old in-tree drivers worked: every cluster
   was a Heat stack; nodes were configured by large shell fragments
   delivered through cloud-init and Heat software deployments.

::

   magnum-conductor
        |
        |  render HOT templates + shell fragments
        v
   +---------+   creates   +------------------------------------+
   |  Heat   |------------>| Nova servers, Neutron, Octavia,    |
   |  stack  |             | Cinder ... + SoftwareDeployments   |
   +---------+             +------------------------------------+
                                       |
                            boot scripts install k8s
                            (one set per distro / k8s version)

Why Heat had to go
==================
.. container:: handout

   ~2:00. Do not bash Heat -- it served Magnum for years. The problem
   was that Magnum re-implemented a Kubernetes installer in Heat
   templates and shell, and had to keep chasing upstream Kubernetes,
   distros and container runtimes with a small team.

.. container:: progressive

   * Magnum maintained its own Kubernetes installer in HOT + bash
   * Tied to specific distro images (Fedora CoreOS) and k8s versions
   * Upgrades and resizes were fragile stack updates
   * Hard dependency on Heat being deployed and healthy
   * Kubernetes lifecycle tooling moved on: *Cluster API*
   * Small team: maintaining a parallel installer did not scale

Cluster API in 60 seconds
=========================
.. container:: handout

   ~1:00. CAPI = Kubernetes-native, declarative cluster lifecycle.
   A *management cluster* runs controllers that reconcile Cluster,
   Machine, etc. objects into real infrastructure. CAPO is the
   OpenStack provider. Note the key word: management cluster -- we
   will come back to it.

::

   +---------------- management cluster -----------------+
   |  CAPI core   CABPK (bootstrap)   CACPK (ctrl plane) |
   |  CAPO (Cluster API Provider OpenStack)              |
   |                                                     |
   |  Cluster / OpenStackCluster / KubeadmControlPlane   |
   |  MachineDeployment / OpenStackMachine ...           |
   +--------------------------+--------------------------+
                              | reconcile
                              v
          Nova, Neutron, Octavia, Cinder  -->  workload cluster

* Declarative, reconciled, upgradeable by design
* Maintained by the wider Kubernetes community

Pluggable drivers today
=======================
.. container:: handout

   ~1:30. Drivers are discovered via the magnum.drivers entry point
   (Caracal "improve driver discovery"). A template picks its driver
   via the image property or, since the Hibiscus spec, the explicit
   driver field on the cluster template. All COE drivers now live
   out-of-tree.

* Drivers are Python packages registered via stevedore

.. code:: ini

   [entry_points]
   magnum.drivers =
       k8s_capi_helm_v1 = magnum_capi_helm.driver:Driver

* Selected per Cluster Template:

  * ``magnum_driver`` Glance image property, or
  * explicit ``driver`` field on the template

* Magnum core no longer ships a Heat-based COE driver

The driver landscape
====================
.. container:: handout

   ~1:00. Two production CAPI drivers exist out-of-tree. Both share
   one assumption -- someone else built the management cluster.

================== ============== ===================================
Driver             Where          Notes
================== ============== ===================================
magnum-capi-helm   openstack/     StackHPC; Helm charts
                   (official)     (openstack-cluster) on CAPI
magnum-cluster-api vexxhost       CAPI ClusterClass based
k8s_kubeadm_v1     magnum, in-    reference driver; builds CAPI
                   tree (new)     management clusters
================== ============== ===================================

Operators choose -- and can run more than one side by side.

The missing piece
=================
.. container:: handout

   ~1:30. Quote is from the Bobcat clusterapi-driver spec. Every
   deployment today hand-builds a k3s/kind cluster, runs clusterctl
   init by hand, and drops a kubeconfig into magnum.conf.

*"Bootstrapping and managing the external management cluster and
the Cluster API service is out of scope."*
-- Cluster API driver spec (Bobcat)

.. container:: progressive

   * Hand-built k3s / kind cluster, ``clusterctl init`` by hand
   * One static ``[capi_helm] kubeconfig_file`` per deployment
   * No self-service: outside Magnum's API, RBAC and quota
   * No way to spread workload clusters over several mgmt clusters
   * No in-project reference implementation for new drivers / CI

MgmtCluster: a first-class resource
===================================
.. container:: handout

   ~1:30. Part one of the spec, in Magnum core. A MgmtCluster
   relates to a ClusterTemplate exactly like a Cluster does. Only
   templates whose driver declares provides_mgmt_cluster = True can
   be used. An earlier revision used a free-form label on a normal
   Cluster; rejected because it couldn't be listed, quota'd or
   RBAC-scoped separately, and typos went unvalidated.

* New API resource (microversion 1.13)

.. code:: text

   POST   /v1/mgmtclusters        GET /v1/mgmtclusters[/detail]
   GET    /v1/mgmtclusters/{id}   DELETE /v1/mgmtclusters/{id}

* Created from a ClusterTemplate -- same relationship as a Cluster
* Template's driver must declare ``provides_mgmt_cluster = True``
* New ``mgmt_cluster_id`` on ClusterTemplate (default) and
  Cluster (override)
* Core helper for consuming drivers:
  ``get_kubeconfig_for_mgmt_cluster(context, mgmt_cluster_id)``

k8s_kubeadm_v1: the reference driver
====================================
.. container:: handout

   ~1:00. Part two of the spec. Deliberate, narrow exception to the
   out-of-tree-only direction: it exists to be the maintained,
   in-project example of the MgmtCluster bootstrapping pattern, not
   to compete with magnum-capi-helm or magnum-cluster-api.

* Ships **in-tree**: ``magnum/drivers/k8s_kubeadm_v1/``
* Registered via ``magnum.drivers`` like any other driver
* Implements:

.. code:: python

   class Driver(driver.Driver):
       provides_mgmt_cluster = True

       def create_mgmt_cluster(self, context, mgmt_cluster): ...
       def delete_mgmt_cluster(self, context, mgmt_cluster): ...
       def update_mgmt_cluster_status(self, context, mgmt_cluster): ...

* Plain Nova + cloud-init -- no Heat, no Ansible
* Images: ``vexxhost/capo-image-elements`` or image-builder,
  tagged ``magnum_driver=k8s_kubeadm_v1``

Lifecycle: bootstrap
====================
.. container:: handout

   ~1:30. Everything happens on a single Nova server, driven by a
   cloud-init payload the driver generates. Boot from image or from
   volume (boot_from_volume label, size from docker_volume_size).

One Nova server, one cloud-init payload, in order:

.. container:: progressive

   * [1] ``kubeadm init`` -- endpoint = the server's own FIP/fixed IP
   * [2] Remove control-plane taint (single node, no workers)
   * [3] Install CNI -- Kube-OVN by default, label-overridable
   * [4] ``clusterctl init`` *against itself*:
     CAPI core, CABPK, CACPK, CAPO
   * [5] Apply Cluster / OpenStackCluster / KubeadmControlPlane /
     OpenStackMachine describing *this very node*
   * [6] Phone home to Magnum with CA + client cert

The pivot: adopting itself
==========================
.. container:: handout

   ~2:00. The heart of the talk. Classic CAPI: create a throwaway
   kind cluster, use it to build the real mgmt cluster, then
   clusterctl move the objects across. Here there is nothing to move
   from: the node runs CAPI and is described by CAPI objects whose
   OpenStackMachine points (providerID / instanceID) at the Nova
   server that already exists, so CAPO reconciles it as Ready
   instead of creating a new one. The cluster now manages itself.

::

   Classic pivot                      k8s_kubeadm_v1
   -------------                      --------------
   kind (temporary)                   Nova server
     | clusterctl init                  | kubeadm init
     | create target cluster            | clusterctl init (self)
     | clusterctl move  ---->           | apply manifests for
   target cluster                       |   *this* node
     (self-managing)                    v
                                      OpenStackMachine
   delete kind                          providerID = this server
                                        => CAPO: Ready, adopted

* Nothing to ``clusterctl move`` *from* -- the node adopts itself
* No separate long-lived bootstrap cluster to babysit

Phone home, credentials, status
===============================
.. container:: handout

   ~1:00. The phone-home token is analogous to a Heat wait
   condition: single use, short lived, invalidated on use or on
   timeout. Certs go through the normal Magnum cert manager, so
   "openstack coe cluster config" keeps working. Each mgmt cluster
   gets its own application credential -- compromise of one does not
   leak the others, unlike a single shared kubeconfig today.

* **Phone home**: single-use, short-lived token in cloud-init
* CA + client cert stored via ``magnum.common.cert_manager``
  (Barbican by default) -> ``coe cluster config`` just works
* **Application credential** per mgmt cluster, project-scoped,
  created and revoked by the driver -- used by CAPO
* ``MgmtClusterUpdateJob`` polls ``update_mgmt_cluster_status``
  until Nova ``ACTIVE`` + phone-home -> ``CREATE_COMPLETE``
* Delete: server, boot volume, FIP, app credential, certs

Wiring it up
============
.. container:: handout

   ~1:30. Proposed CLI -- python-magnumclient support is a work item,
   not merged yet. Flow: create a template for the kubeadm driver,
   create a mgmt cluster from it, then point a capi-helm template at
   it via mgmt_cluster_id. Consuming drivers fall back to the static
   kubeconfig_file when mgmt_cluster_id is absent, so existing
   deployments keep working.

.. code:: console

   $ openstack coe cluster template create mgmt-tmpl \
       --coe kubernetes --image capo-ubuntu-k8s \
       --flavor m1.large --external-network public
   $ openstack coe mgmt cluster create mgmt-a \
       --cluster-template mgmt-tmpl          # proposed CLI

.. code:: text

   PATCH /v1/clustertemplates/k8s-capi-helm   (default)
     [{"op": "replace", "path": "/mgmt_cluster_id",
       "value": "<mgmt-a uuid>"}]
   POST  /v1/clusters  {..., "mgmt_cluster_id": "<mgmt-b uuid>"}

* No ``mgmt_cluster_id``? Driver falls back to ``kubeconfig_file``

Many management clusters
========================
.. container:: handout

   ~1:00. This is what operators actually gain: isolation,
   smaller blast radius, capacity partitioning, and staged upgrades
   of the CAPI stack itself -- move a template to a newer mgmt
   cluster while old ones keep running.

::

                    +-------------+
                    |   Magnum    |
                    +------+------+
           mgmt_cluster_id |
         +-----------------+-----------------+
         v                 v                 v
   +-----------+     +-----------+     +-----------+
   |  mgmt-a   |     |  mgmt-b   |     |  mgmt-c   |
   |  CAPI vN  |     |  CAPI vN  |     |  CAPI vN+1|
   +-----+-----+     +-----+-----+     +-----+-----+
     |   |   |           |   |               |
    wl  wl  wl          wl  wl              wl   (workload clusters)

* Isolation and blast-radius reduction per tenant / region / tier
* Capacity partitioning
* Staged upgrades of the management plane itself

v1 scope, honestly
==================
.. container:: handout

   ~1:00. Be upfront. HA was rejected for v1 on complexity grounds:
   etcd join sequencing and a load-balanced controlPlaneEndpoint
   that cloud-init alone can't configure. Self-adoption must be
   proven first. Upgrades will likely use CAPI's own kubeadm upgrade
   machinery once the node is self-managed.

* Single control-plane node -- no HA mgmt cluster yet
* No resize / upgrade of the mgmt cluster in v1
  (``ClusterOperationNotSupported``)
* ``MgmtCluster`` is immutable -- no ``PATCH``
* ``coe=kubernetes`` only
* A mgmt cluster is a *high-value target*: its CAPO credential can
  touch every workload cluster that names it

Future: HA, in-place upgrades via CAPI kubeadm machinery

Alternatives we rejected
========================
.. container:: handout

   ~0:45. Quick slide; useful for the Q&A.

.. container:: progressive

   * **Status quo** -- manual mgmt clusters forever
   * **Heat or Ansible** for the mgmt cluster -- reintroduces what we
     just removed, or a new execution model in the conductor
   * **HA from day one** -- too complex before self-adoption is proven
   * **Just a label on a normal Cluster** -- can't be listed, quota'd
     or RBAC-scoped separately; typos go unvalidated

What's next for Magnum
======================
.. container:: handout

   ~1:30. Other open magnum-specs reviews. HCP (Kamaji / K0smotron)
   hosts tenant control planes as pods on a management cluster -- a
   natural consumer of MgmtCluster. Add-ons spec moves add-on
   selection to CAPI Cluster labels consumed by Sveltos or CAAPH, and
   introduces a generic discovery mechanism others can reuse. The
   last three are API quality-of-life improvements that let drivers
   own more of the logic.

Open specs at review.opendev.org (magnum-specs):

* **Hosted Control Planes** -- Kamaji / K0smotron drivers, control
  planes as pods on a management cluster
* **Add-ons management** -- ``addons`` field -> CAPI Cluster labels,
  reconciled by Sveltos or CAAPH; ``openstack coe addon list``
* **Upgrade candidates API** -- ``GET /clusters/{id}/upgrade``
* **Driver-side API validation** -- immediate, driver-specific errors
* **Label normalisation** -- clear label inheritance across upgrades

Takeaways
=========
.. container:: handout

   ~0:30. Wrap up and go to Q&A.

.. container:: progressive

   * Heat is gone; Magnum is a thin, pluggable control plane
   * Pick the CAPI driver that fits -- or run several
   * ``MgmtCluster`` makes management clusters a Magnum resource
   * ``k8s_kubeadm_v1`` bootstraps one and lets it adopt itself
   * ``mgmt_cluster_id`` lets each template / cluster choose its
     management plane

Thank you -- questions?
=======================
.. container:: handout

   Q&A.

Specs, reviews and feedback welcome:

* review.opendev.org/q/project:openstack/magnum-specs
* opendev.org/openstack/magnum
* opendev.org/openstack/magnum-capi-helm
* github.com/vexxhost/magnum-cluster-api

#openstack-containers on OFTC

Michal Nasiadka -- StackHPC -- michal@stackhpc.com
