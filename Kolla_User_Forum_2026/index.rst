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

      Michal Nasiadka · Bartosz Bezak

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

      AZs from inventory

      Nova host aggregates and availability zones managed by Kolla-Ansible

   .. container:: card magnum fragment

      libvirt: rotated logs, parallel builds

      virtlogd rotates console logs; higher request limits stop
      concurrent builds failing

   .. container:: card legacy fragment

      Housekeeping

      CentOS Stream 10 and networking-infoblox removed; ``keystone``
      container renamed to ``keystone-api``

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

      Jinja2 macros in each Dockerfile clean up repos and re-enable the
      base OS repos, so child images keep access to base packages

.. container:: callout danger fragment

   RPM repos sharing one ``.repo`` file (same ``file_group``) must be
   overridden together, or the others are silently disabled.

.. revealjs-notes::

   The macros (kolla_cleanup_repos(), kolla_enable_base_repos()) replace
   the Python-level injection in kolla_worker.py. Base repos are explicitly
   re-enabled in every service image so child images keep access to base
   OS packages.

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
         * **virtlogd** in ``nova_libvirt``: console logs rotated
           (2 MB × 3) instead of growing forever
         * **libvirt limits raised**: ``max_client_requests`` 5 → 20,
           ``max_workers`` 20 → 50 -- fixes failures on concurrent builds
         * NFS / Quobyte mounts move to ``/var/lib/nova-mnt``; mount leak
           fixed

   .. container:: col

      .. code-block:: yaml

         # host_vars/compute01
         nova_compute_availability_zone: az-1
         nova_compute_aggregates:
           - gpu-v100
           - ssd-storage

      .. container:: callout fragment

         Existing instances need a **hard reboot** to use virtlogd.

.. revealjs-notes::

   AZs and aggregates (change 988882): set the variables in host_vars or
   group_vars; aggregates are created if missing and memberships are
   reconciled on every deploy / reconfigure. When a host moves AZ it is
   removed from the old AZ aggregate first, but the host must have no
   instances on it -- Nova refuses the change otherwise. See the Nova guide,
   "Host Aggregates and Availability Zones". The
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

      aarch64 IPA over iPXE

      x86_64 and aarch64 nodes each boot their own IPA image from one
      deployment

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

Database and messaging
----------------------

.. container:: section-label

   02 · Kolla-Ansible

.. container:: cards

   .. container:: card capi fragment

      ProxySQL

      Separate CA (``proxysql-ca.pem``) for chained internal TLS; backup
      writer now also serves reads

   .. container:: card capi fragment

      MariaDB backups

      Always taken from ``mariadb_backup_host``, connecting locally; fix
      backported to 2025.1, 2025.2 and 2026.1

   .. container:: card magnum fragment

      RabbitMQ prefetch 1 → 50

      Prefetch 1 serialised quorum-queue consumers; RPC bursts hit false
      ``MessagingTimeout``\s

.. revealjs-notes::

   ProxySQL: writer_is_also_reader=2 (LP#2167037), chained-cert TLS fix
   (LP#2150449). Backups broke with newer MariaDB updates (10.11.19 /
   11.4.13): they were connecting through the load balancer and could lock
   the wrong Galera node. The fix is also in the 2025.1, 2025.2 and 2026.1
   release notes (not 2024.2). New backup names match the restore docs;
   old backups remain restorable.

   RabbitMQ prefetch (om_rabbitmq_qos_prefetch_count, also backported to
   2026.1): 1 was the lowest value oslo.messaging allows with stream
   queues for fanout. With quorum queues on by default, prefetch 1 means
   RabbitMQ delivers the next message to a consumer only after the
   previous one is acked, so nova-conductor, neutron-server, cinder-volume
   etc. process strictly one at a time. With few workers, an RPC burst
   can queue long enough to exceed rpc_response_timeout: a false
   MessagingTimeout with no broker problem. RabbitMQ's quorum queue docs
   recommend higher prefetch. 50 stays > 0 for streams and still bounds
   in-flight messages per consumer; operators can override it.

Removed in Kolla-Ansible
------------------------

.. container:: section-label

   02 · Kolla-Ansible

.. container:: cards two

   .. container:: card legacy fragment

      CentOS Stream 10

      Support dropped (Kolla and Kolla-Ansible)

   .. container:: card legacy fragment

      networking-infoblox

      Infoblox IPAM backend removed -- project unmaintained

   .. container:: card legacy fragment

      OVN DHCP agent

      OVN answers DHCP for bare metal ports natively

   .. container:: card legacy fragment

      JSON policy files

      oslo.policy no longer supports them

.. revealjs-notes::

   Also removed: obsolete Horizon local_settings options (TEMPLATE_DEBUG,
   enable_lb / enable_firewall / enable_vpn under
   OPENSTACK_NEUTRON_NETWORK).

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

Your turn: what should Kolla do next?
-------------------------------------

.. revealjs-section::
   :data-background-image: ../themes/openinfra/bg-dark.png

.. container:: dark columns wide-left

   .. container:: col prompts

      * What hurts in **your** deployment today?
      * Which upgrades were painful -- and why?
      * What features or services should we add next?
      * What's missing from the docs?

   .. container:: col

      Keep the conversation going:

      * ``#openstack-kolla`` on OFTC
      * Bugs and feature requests: bugs.launchpad.net/kolla-ansible
      * Release notes: docs.openstack.org/releasenotes/kolla-ansible

      **Michal Nasiadka** · michal@stackhpc.com

      **Bartosz Bezak** · bartosz@stackhpc.com

      StackHPC

.. revealjs-notes::

   Open discussion -- the main point of the forum. Go through the prompts
   one at a time and capture answers (pain points, upgrade stories,
   feature proposals, doc gaps) for the PTG / weekly meeting. Ask people
   to file bugs or feature requests on Launchpad afterwards so they don't
   get lost.
