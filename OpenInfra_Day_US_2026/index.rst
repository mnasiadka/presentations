Magnum After Heat
=================

.. revealjs-section::
   :data-background-image: ../themes/openinfra/bg-dark.png

.. container:: dark title-slide

   .. container:: headline

      Magnum After Heat

   .. container:: subtitle

      Pluggable Cluster API Drivers and the Road to Self-Managing Kubernetes

   .. container:: speaker

      Michal Nasiadka

      StackHPC · OpenInfra Day US 2026

.. revealjs-notes::

   ~0:30. Introduce yourself. One-sentence pitch: Magnum no longer depends
   on Heat; drivers are pluggable and Cluster API based, and we are adding
   an in-tree reference driver that builds its own management cluster.

Agenda
------

.. container:: section-label

   Topics to talk about

.. container:: topics

   .. container:: topic

      Why Heat had to go

      How Magnum used to build clusters, and why it stopped

   .. container:: topic

      Driver pluggability

      The Cluster API drivers operators can choose today

   .. container:: topic

      Management clusters

      The piece every CAPI driver assumed someone else built

   .. container:: topic

      k8s_kubeadm_v1

      Bootstrap, pivot, self-manage

   .. container:: topic

      What's next

      Hosted control planes, add-ons and API improvements

.. revealjs-notes::

   ~0:20. Four sections, roughly 5 minutes each.

Part 1: Why Heat had to go
--------------------------

.. revealjs-section::
   :data-background-image: ../themes/openinfra/bg-dark.png

.. container:: dark hide-title divider

   .. container:: number

      01

   .. container:: headline

      Why the Heat driver *had to go*

Magnum in one slide
-------------------

.. container:: section-label

   01 · Why Heat had to go

.. raw:: html

   <svg class="diagram" viewBox="0 0 1200 470" role="img"
        aria-label="Magnum architecture: API, conductor and a pluggable driver">
     <defs>
       <marker id="ah1" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
         <path d="M0,0 L10,5 L0,10 z" fill="#161616"/>
       </marker>
     </defs>
     <rect class="box ghost" x="40" y="10" width="340" height="56" rx="28"/>
     <text class="mono" x="210" y="45" text-anchor="middle">openstack coe cluster create</text>
     <path class="arrow" d="M210,66 L210,128" marker-end="url(#ah1)"/>

     <rect class="box magnum" x="40" y="130" width="340" height="100" rx="12"/>
     <text class="title" x="210" y="172" text-anchor="middle">magnum-api</text>
     <text class="sub" x="210" y="202" text-anchor="middle">REST · RBAC · quota</text>

     <rect class="box" x="470" y="130" width="320" height="100" rx="12"/>
     <text class="title" x="630" y="172" text-anchor="middle">Cluster Template</text>
     <text class="sub" x="630" y="202" text-anchor="middle">image · flavors · labels · driver</text>
     <path class="arrow" d="M382,180 L468,180" marker-start="url(#ah1)" marker-end="url(#ah1)"/>

     <path class="arrow" d="M210,230 L210,298" marker-end="url(#ah1)"/>
     <text class="label" x="222" y="270">RPC</text>

     <rect class="box magnum" x="40" y="300" width="340" height="100" rx="12"/>
     <text class="title" x="210" y="342" text-anchor="middle">magnum-conductor</text>
     <text class="sub" x="210" y="372" text-anchor="middle">periodic status sync</text>

     <rect class="box capi" x="470" y="300" width="320" height="100" rx="12"/>
     <text class="title" x="630" y="342" text-anchor="middle">driver</text>
     <text class="sub" x="630" y="372" text-anchor="middle">pluggable · out-of-tree</text>
     <path class="arrow" d="M380,350 L468,350" marker-end="url(#ah1)"/>

     <rect class="box" x="880" y="130" width="290" height="270" rx="12"/>
     <text class="title" x="1025" y="172" text-anchor="middle">Infrastructure</text>
     <text x="1025" y="222" text-anchor="middle">Nova · Neutron</text>
     <text x="1025" y="256" text-anchor="middle">Octavia · Cinder</text>
     <text x="1025" y="290" text-anchor="middle">Keystone</text>
     <text x="1025" y="340" text-anchor="middle">Kubernetes APIs</text>
     <path class="arrow" d="M790,350 L878,350" marker-end="url(#ah1)"/>

     <g class="fragment">
       <rect class="box danger dashed" x="455" y="285" width="350" height="130" rx="18" style="fill:none"/>
       <text class="label-danger" x="630" y="448" text-anchor="middle">the part that changed</text>
     </g>
   </svg>

.. revealjs-notes::

   ~1:00. Set the scene for people who have not touched Magnum. Magnum core
   is an API plus a conductor; the driver does the real work. That split is
   what made it possible to swap Heat out. Click: highlight the driver.

The Heat era
------------

.. container:: section-label

   01 · Why Heat had to go

.. raw:: html

   <svg class="diagram" viewBox="0 0 1200 440" role="img"
        aria-label="Heat-based driver: templates rendered into a Heat stack, boot scripts install Kubernetes">
     <defs>
       <marker id="ah2" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
         <path d="M0,0 L10,5 L0,10 z" fill="#161616"/>
       </marker>
     </defs>
     <rect class="box magnum" x="30" y="40" width="270" height="100" rx="12"/>
     <text class="title" x="165" y="82" text-anchor="middle">magnum-conductor</text>
     <text class="sub" x="165" y="112" text-anchor="middle">in-tree Heat driver</text>
     <path class="arrow" d="M300,90 L378,90" marker-end="url(#ah2)"/>

     <rect class="box legacy" x="380" y="40" width="340" height="100" rx="12"/>
     <text class="title" x="550" y="82" text-anchor="middle">HOT templates</text>
     <text class="sub" x="550" y="112" text-anchor="middle">+ hundreds of lines of bash</text>
     <path class="arrow" d="M720,90 L798,90" marker-end="url(#ah2)"/>

     <rect class="box legacy" x="800" y="40" width="370" height="100" rx="12"/>
     <text class="title" x="985" y="82" text-anchor="middle">Heat stack</text>
     <text class="sub" x="985" y="112" text-anchor="middle">one per cluster</text>
     <path class="arrow" d="M985,140 L985,218" marker-end="url(#ah2)"/>

     <rect class="box" x="800" y="220" width="370" height="170" rx="12"/>
     <text class="title" x="985" y="262" text-anchor="middle">OpenStack resources</text>
     <text x="985" y="304" text-anchor="middle">Nova · Neutron · Octavia · Cinder</text>
     <text class="sub" x="985" y="344" text-anchor="middle">+ SoftwareDeployments</text>
     <path class="arrow" d="M800,305 L722,305" marker-end="url(#ah2)"/>

     <rect class="box legacy" x="380" y="250" width="340" height="110" rx="12"/>
     <text class="title" x="550" y="292" text-anchor="middle">boot scripts</text>
     <text class="sub" x="550" y="322" text-anchor="middle">one set per distro &amp; k8s version</text>
     <path class="arrow" d="M380,305 L302,305" marker-end="url(#ah2)"/>

     <rect class="box" x="30" y="250" width="270" height="110" rx="12"/>
     <text class="title" x="165" y="292" text-anchor="middle">Kubernetes</text>
     <text class="sub" x="165" y="322" text-anchor="middle">Fedora CoreOS</text>
   </svg>

.. revealjs-notes::

   ~1:00. Every cluster was a Heat stack; nodes were configured by large
   shell fragments delivered through cloud-init and Heat software
   deployments. Magnum effectively maintained its own Kubernetes installer.

Why Heat had to go
------------------

.. container:: section-label

   01 · Why Heat had to go

.. container:: cards

   .. container:: card legacy fragment

      Own k8s installer

      Magnum maintained a Kubernetes installer in HOT + bash

   .. container:: card legacy fragment

      Pinned to images

      Tied to specific distros (Fedora CoreOS) and k8s versions

   .. container:: card legacy fragment

      Fragile day 2

      Upgrades and resizes were risky stack updates

   .. container:: card legacy fragment

      Hard dependency

      Heat had to be deployed and healthy

   .. container:: card capi fragment

      Ecosystem moved on

      Kubernetes lifecycle tooling converged on Cluster API

   .. container:: card magnum fragment

      Small team

      Maintaining a parallel installer did not scale

.. revealjs-notes::

   ~2:00. Do not bash Heat -- it served Magnum for years. The problem was
   that Magnum re-implemented a Kubernetes installer in Heat templates and
   shell, and had to keep chasing upstream Kubernetes, distros and
   container runtimes with a small team.

Part 2: Driver pluggability
---------------------------

.. revealjs-section::
   :data-background-image: ../themes/openinfra/bg-dark.png

.. container:: dark hide-title divider

   .. container:: number

      02

   .. container:: headline

      Pluggable *Cluster API* drivers

Cluster API in 60 seconds
-------------------------

.. container:: section-label

   02 · Driver pluggability

.. raw:: html

   <svg class="diagram" viewBox="0 0 1200 470" role="img"
        aria-label="Cluster API: controllers in a management cluster reconcile objects into OpenStack resources and a workload cluster">
     <defs>
       <marker id="ah3" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
         <path d="M0,0 L10,5 L0,10 z" fill="#23803a"/>
       </marker>
     </defs>
     <rect class="box capi" x="30" y="20" width="640" height="410" rx="16"/>
     <text class="panel-title" x="55" y="58">MANAGEMENT CLUSTER</text>

     <text class="label" x="55" y="98">controllers</text>
     <rect class="box" x="55" y="110" width="135" height="54" rx="27"/>
     <text x="122" y="144" text-anchor="middle">CAPI core</text>
     <rect class="box" x="205" y="110" width="135" height="54" rx="27"/>
     <text x="272" y="144" text-anchor="middle">CABPK</text>
     <rect class="box" x="355" y="110" width="135" height="54" rx="27"/>
     <text x="422" y="144" text-anchor="middle">CACPK</text>
     <rect class="box" x="505" y="110" width="135" height="54" rx="27"/>
     <text x="572" y="144" text-anchor="middle">CAPO</text>

     <text class="label" x="55" y="208">desired state (Kubernetes objects)</text>
     <rect class="box" x="55" y="222" width="280" height="50" rx="8"/>
     <text class="mono" x="195" y="253" text-anchor="middle">Cluster</text>
     <rect class="box" x="355" y="222" width="285" height="50" rx="8"/>
     <text class="mono" x="497" y="253" text-anchor="middle">OpenStackCluster</text>
     <rect class="box" x="55" y="286" width="280" height="50" rx="8"/>
     <text class="mono" x="195" y="317" text-anchor="middle">KubeadmControlPlane</text>
     <rect class="box" x="355" y="286" width="285" height="50" rx="8"/>
     <text class="mono" x="497" y="317" text-anchor="middle">MachineDeployment</text>
     <rect class="box" x="55" y="350" width="280" height="50" rx="8"/>
     <text class="mono" x="195" y="381" text-anchor="middle">OpenStackMachine</text>
     <rect class="box" x="355" y="350" width="285" height="50" rx="8"/>
     <text class="mono" x="497" y="381" text-anchor="middle">…</text>

     <path class="arrow capi" d="M670,120 L788,120" marker-end="url(#ah3)"/>
     <text class="label-capi" x="729" y="105" text-anchor="middle">reconcile</text>

     <rect class="box" x="790" y="40" width="380" height="150" rx="12"/>
     <text class="title" x="980" y="90" text-anchor="middle">OpenStack</text>
     <text x="980" y="130" text-anchor="middle">Nova · Neutron</text>
     <text x="980" y="162" text-anchor="middle">Octavia · Cinder</text>
     <path class="arrow capi" d="M980,190 L980,258" marker-end="url(#ah3)"/>

     <rect class="box magnum" x="790" y="260" width="380" height="170" rx="12"/>
     <text class="title" x="980" y="302" text-anchor="middle">workload cluster</text>
     <rect class="box" x="840" y="330" width="80" height="70" rx="8"/>
     <rect class="box" x="940" y="330" width="80" height="70" rx="8"/>
     <rect class="box" x="1040" y="330" width="80" height="70" rx="8"/>

     <g class="fragment">
       <rect class="box danger dashed" x="18" y="8" width="664" height="434" rx="22" style="fill:none"/>
       <text class="label-danger" x="350" y="465" text-anchor="middle">…but who builds and runs this cluster?</text>
     </g>
   </svg>

.. revealjs-notes::

   ~1:00. CAPI is Kubernetes-native, declarative cluster lifecycle. A
   management cluster runs controllers that reconcile Cluster, Machine,
   etc. objects into real infrastructure. CAPO is the OpenStack provider.
   Click: the question that drives the rest of the talk.

Pluggable drivers today
-----------------------

.. container:: section-label

   02 · Driver pluggability

.. container:: columns

   .. container:: col

      .. revealjs-fragments::

         * Drivers are Python packages, discovered via stevedore
         * Selected per Cluster Template

           * ``magnum_driver`` image property
           * or the explicit ``driver`` field

         * Magnum core no longer ships a Heat COE driver
         * Operators pick -- and can run several side by side

   .. container:: col

      .. code-block:: ini

         # setup.cfg of a driver package
         [entry_points]
         magnum.drivers =
             k8s_capi_helm_v1 =
                 magnum_capi_helm.driver:Driver

      .. code-block:: console

         $ openstack image set ubuntu-k8s \
             --property magnum_driver=k8s_capi_helm_v1

.. revealjs-notes::

   ~1:30. Drivers are discovered via the magnum.drivers entry point
   (Caracal "improve driver discovery"). A template picks its driver via
   the image property or, since the Hibiscus spec, the explicit driver
   field on the cluster template. All COE drivers now live out-of-tree.

The driver landscape
--------------------

.. container:: section-label

   02 · Driver pluggability

.. container:: cards

   .. container:: card capi

      magnum-capi-helm

      ``openstack/magnum-capi-helm`` · StackHPC

      Helm charts (``openstack-cluster``) on Cluster API

   .. container:: card capi

      magnum-cluster-api

      ``vexxhost/magnum-cluster-api``

      Cluster API with ClusterClass

   .. container:: card magnum fragment

      k8s_kubeadm_v1  (new)

      In-tree in ``openstack/magnum``

      Reference driver that *builds CAPI management clusters*

.. container:: callout fragment

   Both existing drivers share one assumption:
   **someone else already built the management cluster.**

.. revealjs-notes::

   ~1:00. Two production CAPI drivers exist out-of-tree. Both rely on an
   externally built management cluster -- which leads to the gap.

Part 3: Management clusters
---------------------------

.. revealjs-section::
   :data-background-image: ../themes/openinfra/bg-dark.png

.. container:: dark hide-title divider

   .. container:: number

      03

   .. container:: headline

      The missing piece: *management clusters*

The missing piece
-----------------

.. container:: section-label

   03 · Management clusters

.. container:: quote

   "Bootstrapping and managing the external management cluster and the
   Cluster API service is **out of scope**."

   .. container:: attribution

      -- Cluster API driver spec (Bobcat)

.. raw:: html

   <svg class="diagram" viewBox="0 0 1200 300" role="img"
        aria-label="Today: Magnum's driver uses a static kubeconfig for a hand-built management cluster outside Magnum">
     <defs>
       <marker id="ah4" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
         <path d="M0,0 L10,5 L0,10 z" fill="#161616"/>
       </marker>
     </defs>
     <rect class="box magnum" x="30" y="90" width="250" height="100" rx="12"/>
     <text class="title" x="155" y="148" text-anchor="middle">Magnum</text>
     <path class="arrow" d="M280,140 L368,140" marker-end="url(#ah4)"/>

     <rect class="box capi" x="370" y="90" width="320" height="100" rx="12"/>
     <text class="title" x="530" y="132" text-anchor="middle">magnum-capi-helm</text>
     <text class="mono" x="530" y="164" text-anchor="middle">kubeconfig_file =</text>
     <path class="arrow dashed" d="M690,140 L778,140" marker-end="url(#ah4)"/>

     <rect class="box danger dashed" x="780" y="50" width="390" height="180" rx="16"/>
     <text class="title" x="975" y="105" text-anchor="middle">hand-built mgmt cluster</text>
     <text class="sub" x="975" y="140" text-anchor="middle">k3s / kind · clusterctl init by hand</text>
     <text class="sub" x="975" y="170" text-anchor="middle">one per deployment</text>
     <text class="label-danger" x="975" y="270" text-anchor="middle">outside Magnum's API, RBAC and quota</text>
   </svg>

.. container:: chips fragment

   .. container:: chip

      no self-service

   .. container:: chip

      one static mgmt cluster

   .. container:: chip

      no reference for new drivers / CI

.. revealjs-notes::

   ~1:30. Quote is from the Bobcat clusterapi-driver spec. Every deployment
   today hand-builds a k3s/kind cluster, runs clusterctl init by hand, and
   drops a kubeconfig into magnum.conf. No way to spread workload clusters
   across several management clusters.

MgmtCluster: a first-class resource
-----------------------------------

.. container:: section-label

   03 · Management clusters

.. raw:: html

   <svg class="diagram" viewBox="0 0 1200 330" role="img"
        aria-label="A MgmtCluster is created from a ClusterTemplate; workload templates and clusters reference it by mgmt_cluster_id">
     <defs>
       <marker id="ah5" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
         <path d="M0,0 L10,5 L0,10 z" fill="#161616"/>
       </marker>
       <marker id="ah5b" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
         <path d="M0,0 L10,5 L0,10 z" fill="#1479a8"/>
       </marker>
     </defs>
     <rect class="box" x="30" y="10" width="380" height="96" rx="12"/>
     <text class="title" x="220" y="48" text-anchor="middle">ClusterTemplate</text>
     <text class="mono" x="220" y="80" text-anchor="middle">driver: k8s_kubeadm_v1</text>
     <path class="arrow" d="M220,106 L220,198" marker-end="url(#ah5)"/>
     <text class="label" x="232" y="160">create from</text>

     <rect class="box capi-strong" x="30" y="200" width="380" height="110" rx="12"/>
     <text class="title on-strong" x="220" y="245" text-anchor="middle">MgmtCluster</text>
     <text class="mono" x="220" y="280" text-anchor="middle" style="fill:#fff">/v1/mgmtclusters</text>

     <g class="fragment">
       <rect class="box magnum" x="700" y="10" width="470" height="96" rx="12"/>
       <text class="title" x="935" y="48" text-anchor="middle">ClusterTemplate (workload)</text>
       <text class="mono" x="935" y="80" text-anchor="middle">mgmt_cluster_id: default</text>
       <path class="arrow magnum" d="M700,70 C560,70 520,230 412,240" marker-end="url(#ah5b)"/>
     </g>
     <g class="fragment">
       <rect class="box magnum" x="700" y="200" width="470" height="110" rx="12"/>
       <text class="title" x="935" y="245" text-anchor="middle">Cluster</text>
       <text class="mono" x="935" y="280" text-anchor="middle">mgmt_cluster_id: override</text>
       <path class="arrow magnum" d="M700,265 L412,265" marker-end="url(#ah5b)"/>
     </g>
   </svg>

.. container:: columns

   .. container:: col small

      * New API, microversion **1.13**: create / list / show / delete
      * Template driver must set ``provides_mgmt_cluster = True``

   .. container:: col small

      * Consuming drivers call
        ``get_kubeconfig_for_mgmt_cluster(context, id)``
      * No ``mgmt_cluster_id``? Fall back to ``kubeconfig_file``

.. revealjs-notes::

   ~1:30. Part one of the spec, in Magnum core. A MgmtCluster relates to a
   ClusterTemplate exactly like a Cluster does. Only templates whose driver
   declares provides_mgmt_cluster = True can be used. Workload templates
   set a default mgmt_cluster_id; clusters can override it. An earlier
   revision used a free-form label on a normal Cluster; rejected because it
   couldn't be listed, quota'd or RBAC-scoped separately.

Part 4: k8s_kubeadm_v1
----------------------

.. revealjs-section::
   :data-background-image: ../themes/openinfra/bg-dark.png

.. container:: dark hide-title divider

   .. container:: number

      04

   .. container:: headline

      Bootstrap, pivot, *self-manage*

k8s_kubeadm_v1: the reference driver
------------------------------------

.. container:: section-label

   04 · k8s_kubeadm_v1

.. container:: columns wide-right

   .. container:: col

      * Ships **in-tree**: ``magnum/drivers/k8s_kubeadm_v1/``
      * Registered like any other driver
      * Plain Nova + cloud-init -- no Heat, no Ansible
      * Images: ``capo-image-elements`` or image-builder

   .. container:: col

      .. code-block:: python

         class Driver(driver.Driver):
             provides_mgmt_cluster = True

             def create_mgmt_cluster(
                     self, context, mgmt_cluster): ...

             def delete_mgmt_cluster(
                     self, context, mgmt_cluster): ...

             def update_mgmt_cluster_status(
                     self, context, mgmt_cluster): ...

.. revealjs-notes::

   ~1:00. Part two of the spec. Deliberate, narrow exception to the
   out-of-tree-only direction: it exists to be the maintained, in-project
   example of the MgmtCluster bootstrapping pattern, not to compete with
   magnum-capi-helm or magnum-cluster-api. Images tagged
   magnum_driver=k8s_kubeadm_v1.

Lifecycle: bootstrap
--------------------

.. container:: section-label

   04 · k8s_kubeadm_v1

One Nova server, one cloud-init payload:

.. container:: steps

   .. container:: step fragment

      kubeadm init

      Endpoint = the server's own floating / fixed IP

   .. container:: step fragment

      Untaint control plane

      Single node, no separate workers

   .. container:: step fragment

      Install CNI

      Kube-OVN by default, label-overridable

   .. container:: step fragment

      clusterctl init -- against itself

      CAPI core, CABPK, CACPK, CAPO

   .. container:: step fragment

      Describe this very node

      Cluster, OpenStackCluster, KubeadmControlPlane, OpenStackMachine

   .. container:: step fragment

      Phone home

      CA + client cert back to Magnum

.. revealjs-notes::

   ~1:30. Everything happens on a single Nova server, driven by a cloud-init
   payload the driver generates. Boot from image or from volume
   (boot_from_volume label, size from docker_volume_size).

The pivot: adopting itself
--------------------------

.. container:: section-label

   04 · k8s_kubeadm_v1

.. raw:: html

   <svg class="diagram" viewBox="0 0 1200 500" role="img"
        aria-label="Classic clusterctl move pivot compared to k8s_kubeadm_v1 self-adoption, where the node's OpenStackMachine points at its own server">
     <defs>
       <marker id="ah6" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
         <path d="M0,0 L10,5 L0,10 z" fill="#a3a8ad"/>
       </marker>
       <marker id="ah6c" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
         <path d="M0,0 L10,5 L0,10 z" fill="#23803a"/>
       </marker>
     </defs>

     <rect class="box panel" x="10" y="0" width="420" height="490" rx="16"/>
     <text class="panel-title" x="35" y="40">CLASSIC PIVOT</text>
     <rect class="box ghost dashed" x="50" y="80" width="340" height="80" rx="12"/>
     <text class="title" x="220" y="115" text-anchor="middle" style="fill:#5b6168">kind</text>
     <text class="sub" x="220" y="142" text-anchor="middle">temporary bootstrap cluster</text>
     <path class="arrow muted" d="M220,160 L220,268" marker-end="url(#ah6)"/>
     <text class="label" x="232" y="205">clusterctl init</text>
     <text class="label" x="232" y="230">create target</text>
     <rect class="box ghost" x="50" y="270" width="340" height="80" rx="12"/>
     <text class="title" x="220" y="318" text-anchor="middle" style="fill:#5b6168">target cluster</text>
     <path class="arrow muted" d="M390,120 C470,160 470,270 392,305" marker-end="url(#ah6)"/>
     <text class="label" x="415" y="380" text-anchor="end">clusterctl move</text>
     <text class="sub" x="220" y="440" text-anchor="middle">then delete kind</text>

     <rect class="box capi" x="460" y="0" width="730" height="490" rx="16" style="fill:#fff"/>
     <text class="panel-title" x="485" y="40" style="fill:#23803a">K8S_KUBEADM_V1: SELF-ADOPTION</text>

     <rect class="box" x="490" y="65" width="380" height="400" rx="14"/>
     <text class="title" x="680" y="100" text-anchor="middle">Nova server</text>
     <text class="sub" x="680" y="126" text-anchor="middle">single node</text>

     <g class="fragment">
       <rect class="box capi" x="515" y="145" width="330" height="60" rx="10"/>
       <text x="680" y="183" text-anchor="middle">kubeadm init + CNI</text>
     </g>
     <g class="fragment">
       <rect class="box capi" x="515" y="220" width="330" height="60" rx="10"/>
       <text x="680" y="258" text-anchor="middle">CAPI + CAPO (clusterctl init → self)</text>
     </g>
     <g class="fragment">
       <rect class="box capi-strong" x="515" y="295" width="330" height="80" rx="10"/>
       <text class="mono" x="680" y="328" text-anchor="middle" style="fill:#fff">OpenStackMachine</text>
       <text class="mono" x="680" y="356" text-anchor="middle" style="fill:#fff">providerID: this server</text>
     </g>
     <g class="fragment">
       <path class="arrow capi" d="M845,335 C1000,335 1000,90 872,90" marker-end="url(#ah6c)"/>
       <text class="label-capi" x="990" y="200">points at</text>
       <text class="label-capi" x="990" y="224">itself</text>
       <rect class="box capi-strong" x="900" y="390" width="260" height="60" rx="30"/>
       <text class="on-strong" x="1030" y="428" text-anchor="middle">Ready · adopted</text>
     </g>
   </svg>

.. container:: callout fragment

   Nothing to ``clusterctl move`` *from* -- no long-lived bootstrap cluster to babysit.

.. revealjs-notes::

   ~2:00. The heart of the talk. Classic CAPI: create a throwaway kind
   cluster, use it to build the real mgmt cluster, then clusterctl move the
   objects across. Here there is nothing to move from: the node runs CAPI
   and is described by CAPI objects whose OpenStackMachine points
   (providerID / instanceID) at the Nova server that already exists, so
   CAPO reconciles it as Ready instead of creating a new one. Click through
   the layers, then the self-reference.

Phone home, credentials, status
-------------------------------

.. container:: section-label

   04 · k8s_kubeadm_v1

.. raw:: html

   <svg class="diagram" viewBox="0 0 1200 360" role="img"
        aria-label="Sequence: the node phones home to Magnum with a single-use token; certs go to Barbican; a periodic job marks the cluster complete">
     <defs>
       <marker id="ah7" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
         <path d="M0,0 L10,5 L0,10 z" fill="#161616"/>
       </marker>
     </defs>
     <rect class="box capi" x="70" y="0" width="260" height="56" rx="10"/>
     <text class="title" x="200" y="37" text-anchor="middle">mgmt node</text>
     <rect class="box magnum" x="470" y="0" width="260" height="56" rx="10"/>
     <text class="title" x="600" y="37" text-anchor="middle">Magnum</text>
     <rect class="box" x="870" y="0" width="260" height="56" rx="10"/>
     <text class="title" x="1000" y="37" text-anchor="middle">Barbican</text>
     <path class="lifeline" d="M200,56 L200,350"/>
     <path class="lifeline" d="M600,56 L600,350"/>
     <path class="lifeline" d="M1000,56 L1000,350"/>

     <g class="fragment">
       <path class="arrow" d="M600,105 L204,105" marker-end="url(#ah7)"/>
       <text x="400" y="93" text-anchor="middle" style="font-size:19px">cloud-init: single-use token + app credential</text>
     </g>
     <g class="fragment">
       <path class="arrow" d="M200,175 L596,175" marker-end="url(#ah7)"/>
       <text x="400" y="163" text-anchor="middle" style="font-size:19px">phone home: CA + client cert</text>
     </g>
     <g class="fragment">
       <path class="arrow" d="M600,245 L996,245" marker-end="url(#ah7)"/>
       <text x="800" y="233" text-anchor="middle" style="font-size:19px">store via cert_manager</text>
     </g>
     <g class="fragment">
       <path class="arrow" d="M600,295 C680,295 680,335 604,335" marker-end="url(#ah7)"/>
       <text x="690" y="322" style="font-size:19px">MgmtClusterUpdateJob → CREATE_COMPLETE</text>
     </g>
   </svg>

.. container:: columns

   .. container:: col small

      * Token is single-use and short-lived, like a Heat wait condition
      * ``openstack coe cluster config`` keeps working

   .. container:: col small

      * Per-cluster, project-scoped app credential for CAPO
      * Delete removes server, volume, FIP, credential, certs

.. revealjs-notes::

   ~1:00. Token is invalidated on first use or on create-timeout. Certs go
   through the normal Magnum cert manager (Barbican by default). Each mgmt
   cluster gets its own application credential -- compromise of one does
   not leak the others, unlike a single shared kubeconfig today.

Wiring it up
------------

.. container:: section-label

   04 · k8s_kubeadm_v1

.. code-block:: console

   $ openstack coe cluster template create mgmt-tmpl \
       --coe kubernetes --image capo-ubuntu-k8s \
       --flavor m1.large --external-network public
   $ openstack coe mgmt cluster create mgmt-a \
       --cluster-template mgmt-tmpl                 # proposed CLI

.. code-block:: text

   PATCH /v1/clustertemplates/k8s-capi-helm            # template default
     [{"op": "replace", "path": "/mgmt_cluster_id", "value": "<mgmt-a>"}]

   POST  /v1/clusters  {..., "mgmt_cluster_id": "<mgmt-b>"}   # per-cluster override

.. container:: callout fragment

   No ``mgmt_cluster_id``? Consuming drivers fall back to the static
   ``kubeconfig_file`` -- existing deployments keep working.

.. revealjs-notes::

   ~1:30. Proposed CLI -- python-magnumclient support is a work item, not
   merged yet. Flow: template for the kubeadm driver, mgmt cluster from it,
   then point a capi-helm template at it via mgmt_cluster_id.

Many management clusters
------------------------

.. container:: section-label

   04 · k8s_kubeadm_v1

.. raw:: html

   <svg class="diagram" viewBox="0 0 1200 420" role="img"
        aria-label="One Magnum, several management clusters selected by mgmt_cluster_id, each with its own workload clusters">
     <defs>
       <marker id="ah8" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
         <path d="M0,0 L10,5 L0,10 z" fill="#1479a8"/>
       </marker>
     </defs>
     <rect class="box magnum" x="450" y="0" width="300" height="76" rx="12"/>
     <text class="title" x="600" y="47" text-anchor="middle">Magnum</text>
     <text class="label" x="770" y="45">mgmt_cluster_id</text>

     <path class="arrow magnum" d="M520,76 L230,168" marker-end="url(#ah8)"/>
     <rect class="box capi" x="70" y="170" width="320" height="100" rx="12"/>
     <text class="title" x="230" y="212" text-anchor="middle">mgmt-a</text>
     <text class="sub" x="230" y="242" text-anchor="middle">CAPI vN · tenant A</text>
     <rect class="box magnum" x="85" y="330" width="80" height="60" rx="8"/>
     <rect class="box magnum" x="190" y="330" width="80" height="60" rx="8"/>
     <rect class="box magnum" x="295" y="330" width="80" height="60" rx="8"/>
     <path class="arrow muted" d="M125,270 L125,330 M230,270 L230,330 M335,270 L335,330"/>

     <g class="fragment">
       <path class="arrow magnum" d="M600,76 L600,168" marker-end="url(#ah8)"/>
       <rect class="box capi" x="440" y="170" width="320" height="100" rx="12"/>
       <text class="title" x="600" y="212" text-anchor="middle">mgmt-b</text>
       <text class="sub" x="600" y="242" text-anchor="middle">CAPI vN · region 2</text>
       <rect class="box magnum" x="505" y="330" width="80" height="60" rx="8"/>
       <rect class="box magnum" x="615" y="330" width="80" height="60" rx="8"/>
       <path class="arrow muted" d="M545,270 L545,330 M655,270 L655,330"/>
     </g>
     <g class="fragment">
       <path class="arrow magnum" d="M680,76 L970,168" marker-end="url(#ah8)"/>
       <rect class="box capi-strong" x="810" y="170" width="320" height="100" rx="12"/>
       <text class="title on-strong" x="970" y="212" text-anchor="middle">mgmt-c</text>
       <text x="970" y="242" text-anchor="middle" style="fill:#fff;font-size:18px">CAPI vN+1 · staged upgrade</text>
       <rect class="box magnum" x="930" y="330" width="80" height="60" rx="8"/>
       <path class="arrow muted" d="M970,270 L970,330"/>
     </g>
   </svg>

.. container:: chips fragment

   .. container:: chip

      isolation & smaller blast radius

   .. container:: chip

      capacity partitioning

   .. container:: chip

      staged upgrades of the CAPI stack

.. revealjs-notes::

   ~1:00. This is what operators actually gain: isolation, smaller blast
   radius, capacity partitioning, and staged upgrades of the CAPI stack
   itself -- move a template to a newer mgmt cluster while old ones keep
   running.

v1 scope, honestly
------------------

.. container:: section-label

   04 · k8s_kubeadm_v1

.. container:: cards two

   .. container:: card capi

      In v1

      Single-node, self-adopting mgmt cluster; create / delete;
      boot from image or volume; ``coe=kubernetes``

   .. container:: card legacy

      Not yet

      HA mgmt clusters; resize and upgrade
      (``ClusterOperationNotSupported``); ``PATCH`` -- immutable in v1

.. container:: callout danger fragment

   A mgmt cluster is a **high-value target**: its CAPO credential can touch
   every workload cluster that names it.

.. container:: muted small fragment

   Future: HA, and in-place upgrades via CAPI's own kubeadm machinery once
   the node is self-managed.

.. revealjs-notes::

   ~1:00. Be upfront. HA was rejected for v1 on complexity grounds: etcd
   join sequencing and a load-balanced controlPlaneEndpoint that cloud-init
   alone can't configure. Self-adoption must be proven first.

Alternatives we rejected
------------------------

.. container:: section-label

   04 · k8s_kubeadm_v1

.. container:: cards two

   .. container:: card fragment

      Status quo

      Manual mgmt clusters forever -- the problem we are solving

   .. container:: card fragment

      Heat or Ansible

      Reintroduces what we just removed, or a new execution model in the
      conductor

   .. container:: card fragment

      HA from day one

      Too complex before self-adoption is proven

   .. container:: card fragment

      A label on a normal Cluster

      Can't be listed, quota'd or RBAC-scoped separately; typos go
      unvalidated

.. revealjs-notes::

   ~0:45. Quick slide; useful for the Q&A.

Part 5: What's next
-------------------

.. revealjs-section::
   :data-background-image: ../themes/openinfra/bg-dark.png

.. container:: dark hide-title divider

   .. container:: number

      05

   .. container:: headline

      What's next *for Magnum*

What's next for Magnum
----------------------

.. container:: section-label

   05 · What's next

.. container:: cards

   .. container:: card capi fragment

      Hosted Control Planes

      Kamaji / K0smotron: tenant control planes as pods on a mgmt cluster

   .. container:: card capi fragment

      Add-ons management

      ``addons`` → CAPI Cluster labels, reconciled by Sveltos or CAAPH

   .. container:: card magnum fragment

      Upgrade candidates

      ``GET /clusters/{id}/upgrade``

   .. container:: card magnum fragment

      Driver-side API validation

      Immediate, driver-specific errors

   .. container:: card magnum fragment

      Label normalisation

      Clear label inheritance across upgrades

   .. container:: card fragment

      Your spec here

      review.opendev.org -- ``openstack/magnum-specs``

.. revealjs-notes::

   ~1:30. Other open magnum-specs reviews. HCP hosts tenant control planes
   as pods on a management cluster -- a natural consumer of MgmtCluster.
   Add-ons moves selection to CAPI Cluster labels and adds a generic
   discovery mechanism. The last three are API quality-of-life
   improvements that let drivers own more of the logic.

Takeaways
---------

.. container:: section-label

   05 · What's next

.. revealjs-fragments::

   * Heat is gone; Magnum is a thin, pluggable control plane
   * Pick the CAPI driver that fits -- or run several
   * ``MgmtCluster`` makes management clusters a Magnum resource
   * ``k8s_kubeadm_v1`` bootstraps one and lets it **adopt itself**
   * ``mgmt_cluster_id`` lets each template / cluster choose its
     management plane

.. revealjs-notes::

   ~0:30. Wrap up and go to Q&A.

Thank you -- questions?
-----------------------

.. revealjs-section::
   :data-background-image: ../themes/openinfra/bg-dark.png

.. container:: dark columns

   .. container:: col

      Specs, reviews and feedback welcome:

      * review.opendev.org/q/project:openstack/magnum-specs
      * opendev.org/openstack/magnum
      * opendev.org/openstack/magnum-capi-helm
      * github.com/vexxhost/magnum-cluster-api

   .. container:: col

      ``#openstack-containers`` on OFTC

      **Michal Nasiadka** · StackHPC

      michal@stackhpc.com

.. revealjs-notes::

   Q&A.
