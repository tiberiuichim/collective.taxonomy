# -*- coding: utf-8 -*-
from collective.taxonomy.testing import INTEGRATION_TESTING
from collective.taxonomy.interfaces import ITaxonomy
from plone import api
from plone.app.querystring.interfaces import IQuerystringRegistryReader
from plone.app.testing import applyProfile
from plone.registry.interfaces import IRegistry
from zope.component import queryUtility
import unittest


class TestIndexer(unittest.TestCase):

    """Test JSON views."""

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.portal.portal_workflow.setDefaultChain(
            'simple_publication_workflow')
        applyProfile(self.portal, 'plone.app.contenttypes:plone-content')
        self.document = api.content.create(
            container=self.portal, type='Document', title='Doc', language='en')

    def test_indexer_with_field(self):
        portal_catalog = api.portal.get_tool('portal_catalog')
        utility = queryUtility(ITaxonomy, name='collective.taxonomy.test')
        taxonomy = utility.data

        index = portal_catalog.Indexes['taxonomy_test']
        self.assertEqual(index.numObjects(), 0)

        self.document.taxonomy_test = []
        self.document.reindexObject()
        query = {'taxonomy_test': '1'}
        self.assertEqual(len(portal_catalog(query)), 0)

        taxo_val = taxonomy['en'][u'\u241fInformation Science\u241fChronology']
        self.document.taxonomy_test = [taxo_val]
        self.document.reindexObject()
        self.assertEqual(len(portal_catalog(query)), 1)
        index = portal_catalog.Indexes['taxonomy_test']
        self.assertEqual(index.numObjects(), 1)

        self.document.taxonomy_test = set(taxo_val)
        self.document.reindexObject()
        index = portal_catalog.Indexes['taxonomy_test']
        self.assertEqual(index.numObjects(), 1)

    def test_multilanguage_indexer(self):
        portal_catalog = api.portal.get_tool('portal_catalog')
        utility = queryUtility(ITaxonomy, name='collective.taxonomy.test')
        taxonomy = utility.data
        query = {'taxonomy_test': '5'}
        taxo_val = taxonomy['en'][u'\u241fInformation Science\u241fSport']
        self.document.taxonomy_test = [taxo_val]
        self.document.reindexObject()
        self.assertEqual(len(portal_catalog(query)), 1)

    def test_querystring_widget(self):
        registry = queryUtility(IRegistry)
        config = IQuerystringRegistryReader(registry)()
        self.assertEqual(
            sorted(config['indexes']['taxonomy_test']['values'].items()),
            [('1', {'title': u'Information Science'}),
             ('2', {'title': u'Information Science \xbb Book Collecting'}),
             ('3', {'title': u'Information Science \xbb Chronology'}),
             ('5', {'title': u'Information Science \xbb Sport'})]
        )
