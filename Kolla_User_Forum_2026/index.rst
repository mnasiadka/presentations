Kolla 2026.2
============

.. revealjs-section::
   :data-background-image: ../themes/openinfra/bg-dark.png

.. container:: dark title-slide

   .. container:: headline

      Kolla & Kolla-Ansible 2026.2

   .. container:: subtitle

      What's new in Hibiscus (23.0.0)

   .. container:: speaker

      Michal Nasiadka

      StackHPC · Kolla User Forum

.. revealjs-notes::

   Release summary for Kolla and Kolla-Ansible 23.0.0 (2026.2 Hibiscus),
   based on the published release notes including the 23.0.0-4 (Kolla) and
   23.0.0-6 (Kolla-Ansible) updates.

At a glance
-----------

.. container:: section-label

   2026.2 Hibiscus · 23.0.0

.. container:: stats-caption

   Kolla -- container images

.. container:: stats

   .. container:: stat capi

      14

      new features

   .. container:: stat legacy

      41

      upgrade notes (mostly version bumps)

   .. container:: stat magnum

      8

      bug fixes

.. container:: stats-caption

   Kolla-Ansible -- deployment

.. container:: stats

   .. container:: stat capi

      13

      new features

   .. container:: stat legacy

      15

      upgrade notes

   .. container:: stat magnum

      36

      bug fixes

.. revealjs-notes::

   Counts are top-level entries in the 2026.2 release notes pages. Most of
   Kolla's upgrade notes are component version bumps (Prometheus exporters,
   etcd, lego, ...). Kolla-Ansible's headline is the number of bug fixes.

Highlights
----------

.. container:: section-label

   2026.2 Hibiscus · 23.0.0

.. container:: cards

   .. container:: card capi fragment

      BuildKit by default

      ``docker buildx`` builds, multi-arch via named builders

   .. container:: card capi fragment

      Repositories as data

      Base OS repos in ``repos.yaml``, overridable for local mirrors

   .. container:: card magnum fragment

      Kerbside

      Native SPICE proxy for high-fidelity VDI consoles

   .. container:: card magnum fragment

      AZs from inventory

      Nova host aggregates and availability zones managed by Kolla-Ansible

   .. container:: card magnum fragment

      Calmer libvirt

      virtlogd log rotation, higher request limits, fewer build failures

   .. container:: card legacy fragment

      Housekeeping

      CentOS Stream 10, networking-infoblox, Redis migration code removed

.. revealjs-notes::

   One-slide summary; each card gets its own slide later.

Part 1: Kolla
-------------

.. revealjs-section::
   :data-background-image: ../themes/openinfra/bg-dark.png

.. container:: dark hide-title divider

   .. container:: number

      01

   .. container:: headline

      Kolla: *building images*

Building images
---------------

.. container:: section-label

   01 · Kolla

.. container:: columns

   .. container:: col

      .. revealjs-fragments::

         * **BuildKit** (``docker buildx build``) is the default with
           ``--engine docker``; opt out with ``--nobuildkit``
         * ``--buildkit-builder`` picks a named builder: docker-container
           or remote drivers for multi-arch
         * New ``pip_index_url``, ``pip_trusted_host``,
           ``pip_extra_index_url`` in ``kolla-build.conf``
         * ``build-date`` label is now a build argument -- no daily cache
           invalidation

   .. container:: col

      .. code-block:: console

         $ kolla-build --base rocky \
             --platform linux/amd64,linux/arm64 \
             --buildkit-builder multiarch \
             --push

      .. container:: callout fragment

         **Multi-arch images go to a registry.** Building several
         platforms at once creates one multi-arch image that can't be
         loaded into the local Docker image store, so ``kolla-build``
         requires ``--push`` and errors out without it. Single-platform
         builds load locally as before.

.. revealjs-notes::

   BuildKit needs the docker-buildx-plugin installed and only applies to the
   docker engine. Pip build ARGs are passed via --build-arg so they don't
   persist in the final image. Users overriding LABELs should drop
   build-date from their overrides.

   Why --push: a normal build ends with "--load", importing the image into
   the local Docker image store. A comma-separated --platform list produces
   one multi-arch image (an index of per-architecture images), which buildx
   can't load locally, so the only destination is a registry. Kolla checks
   this up front and fails immediately instead of after a long build.

Repositories as data
--------------------

.. container:: section-label

   01 · Kolla

.. container:: cards two

   .. container:: card capi fragment

      Base OS repos in ``repos.yaml``

      CentOS Stream / Rocky (baseos, appstream, crb) and Debian / Ubuntu
      repos, overridable with ``--repos-yaml`` to point at local mirrors

   .. container:: card capi fragment

      Your ``repos.yaml`` is merged

      No more full copy of the stock file -- override only what you change

   .. container:: card magnum fragment

      Safer overrides

      Existing ``.repo`` files holding an overridden ID are removed;
      Debian/Ubuntu ``gpg_key`` accepts absolute paths (distro keyrings)

   .. container:: card magnum fragment

      Cleanup in the templates

      ``kolla_cleanup_repos()`` and ``kolla_enable_base_repos()`` Jinja2
      macros run before any ``USER`` directive

.. container:: callout danger fragment

   RPM repos sharing one ``.repo`` file (same ``file_group``) must be
   overridden together, or the others are silently disabled.

.. revealjs-notes::

   The macro change replaces the Python-level injection in kolla_worker.py
   and fixes permission errors when non-root service users touched
   root-owned repo files. Base repos are explicitly re-enabled in every
   service image so child images keep access to base OS packages.

Kerbside: SPICE-native consoles
-------------------------------

.. container:: section-label

   01 · Kolla

.. raw:: html

   <svg class="diagram" viewBox="0 0 1200 250" role="img"
        aria-label="A SPICE client connects through the Kerbside proxy to nova-libvirt-spice on the hypervisor">
     <defs>
       <marker id="kah1" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
         <path d="M0,0 L10,5 L0,10 z" fill="#23803a"/>
       </marker>
     </defs>
     <rect class="box" x="20" y="60" width="300" height="120" rx="12"/>
     <text class="title" x="170" y="112" text-anchor="middle">SPICE client</text>
     <text class="sub" x="170" y="142" text-anchor="middle">spice-direct console</text>
     <path class="arrow capi" d="M320,120 L448,120" marker-end="url(#kah1)"/>

     <rect class="box capi-strong" x="450" y="60" width="300" height="120" rx="12"/>
     <text class="title on-strong" x="600" y="112" text-anchor="middle">Kerbside</text>
     <text x="600" y="142" text-anchor="middle" style="fill:#fff;font-size:18px">native SPICE proxy</text>
     <path class="arrow capi" d="M750,120 L878,120" marker-end="url(#kah1)"/>

     <rect class="box capi" x="880" y="60" width="300" height="120" rx="12"/>
     <text class="title" x="1030" y="112" text-anchor="middle">nova-libvirt-spice</text>
     <text class="sub" x="1030" y="142" text-anchor="middle">hypervisor</text>
     <text class="label" x="600" y="225" text-anchor="middle">no HTML5 transcoding in Horizon · no direct access to hypervisor console ports</text>
   </svg>

.. container:: columns

   .. container:: col small

      * New Kerbside images; second libvirt image ``nova-libvirt-spice``
        used when ``enable_kerbside: true``
      * ``nova_spice_require_secure`` forces TLS-secured SPICE channels
        (default ``false``)

   .. container:: col small

      * Rocky: qemu-kvm with SPICE from the community
        ``ligenix/enterprise-qemu-spice`` COPR -- proof of concept only
      * Known issue: no ``usb-audio`` there; use ``ich9`` or ``ac97``

.. revealjs-notes::

   Kerbside exposes Nova's new spice-direct console type for high fidelity
   virtual desktops. The COPR is a third-party rebuild with no vendor
   support. Guests with hw_sound_model=usb fail to start on Rocky with that
   build until it ships usb-audio. nova_spice_require_secure needs TLS
   certificates on the compute nodes.

More in the images
------------------

.. container:: section-label

   01 · Kolla

.. container:: cards

   .. container:: card capi fragment

      YAML configs

      ``kolla_set_configs`` loads ``config.yaml`` as well as
      ``config.json``

   .. container:: card magnum fragment

      keystone → keystone-api

      The ``keystone`` image is replaced by the identical
      ``keystone-api`` image

   .. container:: card magnum fragment

      Ansible

      ansible-core 2.21 in ``kolla-toolbox``

   .. container:: card legacy fragment

      Version bumps

      RabbitMQ 4.3, Prometheus 3.13 LTS, etcd 3.6.15, lego 5.4.1,
      magnum helm plugin 4.3.0

   .. container:: card legacy fragment

      Gone

      CentOS Stream 10 support and the ``neutron-infoblox-ipam-agent``
      image

.. revealjs-notes::

   prometheus-mtail now comes
   from the active fork github.com/jaqx0r/mtail. Plus many exporter bumps
   (node, mysqld, memcached, libvirt, valkey, cadvisor, alertmanager).
   Bug fixes include syslinux in Debian ironic-conductor (ldlinux.c32 for
   redfish-virtual-media), zstd in ironic-conductor, Grafana 13.2
   Prometheus datasource plugin offline, Horizon theme collectstatic.

Part 2: Kolla-Ansible
---------------------

.. revealjs-section::
   :data-background-image: ../themes/openinfra/bg-dark.png

.. container:: dark hide-title divider

   .. container:: number

      02

   .. container:: headline

      Kolla-Ansible: *deploying it*

Nova and libvirt
----------------

.. container:: section-label

   02 · Kolla-Ansible

.. container:: columns

   .. container:: col

      .. revealjs-fragments::

         * **Availability zones and aggregates** from inventory, reconciled
           on every deploy / reconfigure
         * **virtlogd sidecar**: console logs rotated (2 MB × 3) instead of
           growing forever
         * **libvirt limits raised**: ``max_client_requests`` 5 → 20,
           ``max_workers`` 20 → 50 -- fixes failures on concurrent builds
         * NFS / Quobyte mounts move to ``/var/lib/nova-mnt``; mount leak
           fixed

   .. container:: col

      .. code-block:: yaml

         # inventory (YAML)
         compute:
           hosts:
             compute01:
               nova_compute_availability_zone: az1
               nova_compute_aggregates: [gpu, nvme]

      .. container:: callout fragment

         Existing instances need a **hard reboot** to use virtlogd.

.. revealjs-notes::

   Aggregates are created if missing; memberships are reconciled. The
   libvirt limit change fixes "Cannot recv data: Input/output error" during
   defineXML when several instances build at once. Tunables:
   libvirt_max_client_requests, libvirt_max_workers. Also
   nova_scheduler_healthcheck_retries now 8 to cover the 160s worker
   restart window (LP#2162860).

Storage, bare metal, identity
-----------------------------

.. container:: section-label

   02 · Kolla-Ansible

.. container:: cards two

   .. container:: card capi fragment

      VAST

      New backend for both Cinder and Manila

   .. container:: card magnum fragment

      Mixed-arch Ironic

      Architecture-specific IPA images for x86_64 + aarch64 iPXE

   .. container:: card magnum fragment

      Keystone federation

      ``schema_version`` in federated attribute mappings

   .. container:: card legacy fragment

      Service passwords

      ``update_keystone_service_user_passwords`` now defaults to
      ``false`` -- no token invalidation on reconfigure

.. revealjs-notes::

   Set update_keystone_service_user_passwords: true to keep the old
   rotation behaviour.

Database, messaging, monitoring
-------------------------------

.. container:: section-label

   02 · Kolla-Ansible

.. container:: cards

   .. container:: card capi fragment

      ProxySQL

      Separate CA (``proxysql-ca.pem``) for chained internal TLS; backup
      writer now also serves reads

   .. container:: card capi fragment

      MariaDB backups

      Always taken from ``mariadb_backup_host``, connecting locally; fixed
      for 10.11.19 / 11.4.13

   .. container:: card magnum fragment

      RabbitMQ

      ``om_rabbitmq_qos_prefetch_count`` is now 50

   .. container:: card magnum fragment

      Alertmanager

      HAProxy HTTP check on ``/-/healthy`` plus a container healthcheck

   .. container:: card magnum fragment

      Grafana

      Proxy support (``grafana_container_proxy``) and Grafana 13.2 fixes

   .. container:: card magnum fragment

      CloudKitty

      HAProxy client / server timeouts for its unpaginated v1 API

.. revealjs-notes::

   ProxySQL: writer_is_also_reader=2 (LP#2167037), chained-cert TLS fix
   (LP#2150449). Backups were connecting through the load balancer and
   could lock the wrong Galera node. New backup names match the restore
   docs; old backups remain restorable. Grafana: custom home dashboard,
   grafana server instead of grafana-server, duplicated logs fixed.

Removed in Kolla-Ansible
------------------------

.. container:: section-label

   02 · Kolla-Ansible

.. container:: cards

   .. container:: card legacy fragment

      CentOS Stream 10

      Support dropped (Kolla and Kolla-Ansible)

   .. container:: card legacy fragment

      networking-infoblox

      Infoblox IPAM backend removed -- project unmaintained

   .. container:: card legacy fragment

      Legacy Neutron upgrade

      Rolling upgrade only; drop ``neutron_enable_rolling_upgrade``

   .. container:: card legacy fragment

      OVN DHCP agent

      OVN answers DHCP for bare metal ports natively

   .. container:: card legacy fragment

      JSON policy files

      oslo.policy no longer supports them

   .. container:: card legacy fragment

      Redis leftovers

      ``[redis:children]`` and ``redis_master_password`` gone after the
      Valkey migration

.. revealjs-notes::

   Also removed: obsolete Horizon local_settings options (TEMPLATE_DEBUG,
   enable_lb / enable_firewall / enable_vpn under
   OPENSTACK_NEUTRON_NETWORK). The Redis to Valkey migration code had been
   kept since Gazpacho (2026.1).

Fixes worth knowing
-------------------

.. container:: section-label

   02 · Kolla-Ansible

.. container:: columns

   .. container:: col small

      * Instance snapshots no longer hang
      * Concurrent instance builds no longer hit libvirt request limits
      * nova-compute starts after ``/var/lib/nova`` was wiped
      * Glance multinode + internal TLS: no more HTTP 500s on concurrent
        image operations
      * OVN VPNaaS traffic forwarding fixed

   .. container:: col small

      * Fernet key distribution delegated to the right group
      * Retries for container facts / exec during RabbitMQ restarts
      * RabbitMQ precheck accepts the shared backend TLS cert
      * Prometheus precheck works with Ansible Vault values
      * ``kolla-ansible check`` skips unhealthy containers (23.0.0-6)

.. revealjs-notes::

   LP numbers: snapshots LP#2158974, nova-compute after wipe LP#2051011,
   Glance TLS LP#2160218, OVN VPNaaS LP#2160208, fernet LP#2163158,
   container retries LP#2141675, check LP#2156900. 36 bug fixes in total.

Part 3: Upgrading
-----------------

.. revealjs-section::
   :data-background-image: ../themes/openinfra/bg-dark.png

.. container:: dark hide-title divider

   .. container:: number

      03

   .. container:: headline

      Before you *upgrade*

Upgrade checklist
-----------------

.. container:: section-label

   03 · Upgrading

.. container:: columns

   .. container:: col small

      **Kolla-Ansible**

      * Ansible 13--14 (ansible-core 2.20--2.21)
      * ProxySQL + internal DB TLS: provide ``proxysql-ca.pem``
      * Other os-brick Cinder backends: set
        ``enable_cinder_backend_privileged: true``
      * Dedicated NFS filesystem? Mount it at ``/var/lib/nova-mnt``
      * Remove ``redis_master_password``,
        ``neutron_enable_rolling_upgrade``, ``neutron_ovn_dhcp_agent``
      * Convert JSON policy files to YAML

   .. container:: col small

      **Kolla (image builds)**

      * Default ``tag`` is now ``<openstack_release>-<base>-<base_tag>``;
        set ``--tag`` to keep the old one
      * BuildKit is on: needs ``docker-buildx-plugin``
      * Move ``ENV PIP_*`` template overrides to the new pip options
      * Drop ``build-date`` from LABEL overrides
      * ``base_centos_*`` overrides → ``base_rocky_*``

.. revealjs-notes::

   proxysql-ca.pem: copy of the DB internal TLS root CA, or the
   intermediate that signed the leaf when chains are used. The NFS path
   change is non-disruptive: running instances keep the old mount until
   live migration or hard reboot; leftover mounts can then be unmounted
   (busy ones refuse). Hard reboot instances to pick up virtlogd.

Thank you -- questions?
-----------------------

.. revealjs-section::
   :data-background-image: ../themes/openinfra/bg-dark.png

.. container:: dark columns

   .. container:: col

      Release notes:

      * docs.openstack.org/releasenotes/kolla/2026.2.html
      * docs.openstack.org/releasenotes/kolla-ansible/2026.2.html

      Get involved: ``#openstack-kolla`` on OFTC

   .. container:: col

      **Michal Nasiadka** · StackHPC

      michal@stackhpc.com

.. revealjs-notes::

   Q&A.
