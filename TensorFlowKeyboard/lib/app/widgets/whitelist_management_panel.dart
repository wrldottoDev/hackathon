import 'dart:async';

import 'package:flutter/material.dart';

import '../../keyboard/context/trusted_contacts_service.dart';
import '../../src/services/whitelist_service.dart';

class WhitelistManagementPanel extends StatefulWidget {
  const WhitelistManagementPanel({
    super.key,
    required this.trustedContacts,
    required this.whitelist,
  });

  final TrustedContactsService trustedContacts;
  final WhitelistService whitelist;

  @override
  State<WhitelistManagementPanel> createState() =>
      _WhitelistManagementPanelState();
}

class _WhitelistManagementPanelState extends State<WhitelistManagementPanel> {
  final TextEditingController _searchController = TextEditingController();
  String _query = '';

  @override
  void initState() {
    super.initState();
    if (widget.trustedContacts.availableContacts.isEmpty) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        widget.trustedContacts.loadContacts();
      });
    }
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final contacts = widget.trustedContacts.availableContacts.where((contact) {
      final query = _query.trim().toLowerCase();
      if (query.isEmpty) {
        return true;
      }
      return contact.displayName.toLowerCase().contains(query) ||
          (contact.subtitle?.toLowerCase().contains(query) ?? false);
    }).toList(growable: false);

    return AnimatedBuilder(
      animation: Listenable.merge(<Listenable>[
        widget.trustedContacts,
        widget.whitelist,
      ]),
      builder: (context, child) {
        return ListView(
          padding: const EdgeInsets.fromLTRB(16, 18, 16, 18),
          children: <Widget>[
            Text(
              'Whitelist de Contactos',
              style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                    fontWeight: FontWeight.w900,
                  ),
            ),
            const SizedBox(height: 8),
            Text(
              'Selecciona contactos de tu agenda para detener la telemetría local cuando coincidan con la conversación actual. Esta lista se persiste localmente y sincroniza con el ContextManager.',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: const Color(0xFF595952),
                  ),
            ),
            const SizedBox(height: 16),
            _PanelCard(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: <Widget>[
                  Text(widget.trustedContacts.status),
                  const SizedBox(height: 12),
                  Wrap(
                    spacing: 12,
                    runSpacing: 12,
                    children: <Widget>[
                      FilledButton(
                        onPressed: widget.trustedContacts.isLoading
                            ? null
                            : () => widget.trustedContacts.loadContacts(),
                        child: Text(
                          widget.trustedContacts.isLoading
                              ? 'Cargando agenda...'
                              : 'Solicitar / refrescar agenda',
                        ),
                      ),
                      FilledButton.tonal(
                        onPressed: widget.whitelist.contacts.isEmpty
                            ? null
                            : () => widget.whitelist.replaceAll(
                                  const <String>[],
                                ),
                        child: const Text('Vaciar whitelist'),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    controller: _searchController,
                    onChanged: (value) => setState(() {
                      _query = value;
                    }),
                    decoration: const InputDecoration(
                      labelText: 'Buscar contacto',
                      prefixIcon: Icon(Icons.search),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),
            _PanelCard(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: <Widget>[
                  Text(
                    'Seleccionados (${widget.whitelist.contacts.length})',
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.w800,
                        ),
                  ),
                  const SizedBox(height: 12),
                  if (widget.whitelist.contacts.isEmpty)
                    const Text('Todavía no has marcado contactos de confianza.')
                  else
                    Wrap(
                      spacing: 8,
                      runSpacing: 8,
                      children: widget.whitelist.contacts
                          .map(
                            (contact) => InputChip(
                              label: Text(contact),
                              onDeleted: () {
                                unawaited(
                                  widget.whitelist.removeContact(contact),
                                );
                              },
                            ),
                          )
                          .toList(),
                    ),
                ],
              ),
            ),
            const SizedBox(height: 16),
            _PanelCard(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: <Widget>[
                  Text(
                    'Agenda disponible',
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.w800,
                        ),
                  ),
                  const SizedBox(height: 12),
                  if (contacts.isEmpty)
                    const Text('No hay contactos visibles con el filtro actual.')
                  else
                    for (final contact in contacts)
                      CheckboxListTile(
                        value: widget.trustedContacts.isTrusted(contact),
                        contentPadding: EdgeInsets.zero,
                        dense: true,
                        onChanged: (value) => widget.trustedContacts.setTrusted(
                          contact,
                          value ?? false,
                        ),
                        title: Text(contact.displayName),
                        subtitle: contact.subtitle == null
                            ? null
                            : Text(contact.subtitle!),
                      ),
                ],
              ),
            ),
          ],
        );
      },
    );
  }
}

class _PanelCard extends StatelessWidget {
  const _PanelCard({required this.child});

  final Widget child;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: const Color(0xFFD8CDBA)),
      ),
      child: child,
    );
  }
}
