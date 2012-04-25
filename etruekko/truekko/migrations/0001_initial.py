# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'UserProfile'
        db.create_table('truekko_userprofile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('credits', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('name', self.gf('django.db.models.fields.CharField')(default='Unnamed', max_length=100)),
            ('location', self.gf('django.db.models.fields.CharField')(default='Unlocated', max_length=100)),
            ('web', self.gf('django.db.models.fields.URLField')(default='', max_length=200, null=True, blank=True)),
            ('photo', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(max_length=300, blank=True)),
            ('rating_votes', self.gf('django.db.models.fields.PositiveIntegerField')(default=0, blank=True)),
            ('rating_score', self.gf('django.db.models.fields.IntegerField')(default=0, blank=True)),
        ))
        db.send_create_signal('truekko', ['UserProfile'])

        # Adding model 'Group'
        db.create_table('truekko_group', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=500)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('location', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('web', self.gf('django.db.models.fields.URLField')(default='', max_length=200, null=True, blank=True)),
            ('photo', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(max_length=800, blank=True)),
        ))
        db.send_create_signal('truekko', ['Group'])

        # Adding model 'Membership'
        db.create_table('truekko_membership', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['truekko.Group'])),
            ('role', self.gf('django.db.models.fields.CharField')(max_length=3)),
        ))
        db.send_create_signal('truekko', ['Membership'])

        # Adding model 'Transfer'
        db.create_table('truekko_transfer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user_from', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='transfer_from', null=True, to=orm['auth.User'])),
            ('group_from', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='transfer_form', null=True, to=orm['truekko.Group'])),
            ('user_to', self.gf('django.db.models.fields.related.ForeignKey')(related_name='transfer_to', to=orm['auth.User'])),
            ('concept', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('credits', self.gf('django.db.models.fields.IntegerField')()),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('truekko', ['Transfer'])

        # Adding model 'Item'
        db.create_table('truekko_item', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='items', to=orm['auth.User'])),
            ('type', self.gf('django.db.models.fields.CharField')(default='IT', max_length=2)),
            ('demand', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=150)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('price', self.gf('django.db.models.fields.IntegerField')()),
            ('price_type', self.gf('django.db.models.fields.CharField')(default='ETK', max_length=20)),
            ('photo', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
            ('pub_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('truekko', ['Item'])

        # Adding model 'Tag'
        db.create_table('truekko_tag', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('truekko', ['Tag'])

        # Adding model 'ItemTagged'
        db.create_table('truekko_itemtagged', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('item', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['truekko.Item'])),
            ('tag', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['truekko.Tag'])),
        ))
        db.send_create_signal('truekko', ['ItemTagged'])

        # Adding model 'Swap'
        db.create_table('truekko_swap', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user_from', self.gf('django.db.models.fields.related.ForeignKey')(related_name='swaps_from', to=orm['auth.User'])),
            ('user_to', self.gf('django.db.models.fields.related.ForeignKey')(related_name='swaps_to', to=orm['auth.User'])),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=3)),
            ('credits', self.gf('django.db.models.fields.IntegerField')()),
            ('done_msg', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('truekko', ['Swap'])

        # Adding model 'SwapItems'
        db.create_table('truekko_swapitems', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('swap', self.gf('django.db.models.fields.related.ForeignKey')(related_name='items', to=orm['truekko.Swap'])),
            ('item', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['truekko.Item'])),
        ))
        db.send_create_signal('truekko', ['SwapItems'])

        # Adding model 'SwapComment'
        db.create_table('truekko_swapcomment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('swap', self.gf('django.db.models.fields.related.ForeignKey')(related_name='comments', to=orm['truekko.Swap'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('comment', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('truekko', ['SwapComment'])

        # Adding model 'Wall'
        db.create_table('truekko_wall', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='walls', null=True, to=orm['auth.User'])),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='walls', null=True, to=orm['truekko.Group'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(max_length=300, null=True, blank=True)),
        ))
        db.send_create_signal('truekko', ['Wall'])

        # Adding model 'WallMessage'
        db.create_table('truekko_wallmessage', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='messages', to=orm['auth.User'])),
            ('wall', self.gf('django.db.models.fields.related.ForeignKey')(related_name='messages', to=orm['truekko.Wall'])),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('private', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('msg', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('truekko', ['WallMessage'])

        # Adding model 'Denounce'
        db.create_table('truekko_denounce', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user_from', self.gf('django.db.models.fields.related.ForeignKey')(related_name='dennounces_from', to=orm['auth.User'])),
            ('user_to', self.gf('django.db.models.fields.related.ForeignKey')(related_name='dennounces_to', to=orm['auth.User'])),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['truekko.Group'])),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('msg', self.gf('django.db.models.fields.TextField')()),
            ('status', self.gf('django.db.models.fields.CharField')(default='PEN', max_length=3)),
        ))
        db.send_create_signal('truekko', ['Denounce'])

    def backwards(self, orm):
        # Deleting model 'UserProfile'
        db.delete_table('truekko_userprofile')

        # Deleting model 'Group'
        db.delete_table('truekko_group')

        # Deleting model 'Membership'
        db.delete_table('truekko_membership')

        # Deleting model 'Transfer'
        db.delete_table('truekko_transfer')

        # Deleting model 'Item'
        db.delete_table('truekko_item')

        # Deleting model 'Tag'
        db.delete_table('truekko_tag')

        # Deleting model 'ItemTagged'
        db.delete_table('truekko_itemtagged')

        # Deleting model 'Swap'
        db.delete_table('truekko_swap')

        # Deleting model 'SwapItems'
        db.delete_table('truekko_swapitems')

        # Deleting model 'SwapComment'
        db.delete_table('truekko_swapcomment')

        # Deleting model 'Wall'
        db.delete_table('truekko_wall')

        # Deleting model 'WallMessage'
        db.delete_table('truekko_wallmessage')

        # Deleting model 'Denounce'
        db.delete_table('truekko_denounce')

    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'truekko.denounce': {
            'Meta': {'ordering': "['-date']", 'object_name': 'Denounce'},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['truekko.Group']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'msg': ('django.db.models.fields.TextField', [], {}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'PEN'", 'max_length': '3'}),
            'user_from': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'dennounces_from'", 'to': "orm['auth.User']"}),
            'user_to': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'dennounces_to'", 'to': "orm['auth.User']"})
        },
        'truekko.group': {
            'Meta': {'object_name': 'Group'},
            'description': ('django.db.models.fields.TextField', [], {'max_length': '800', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '500'}),
            'photo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'web': ('django.db.models.fields.URLField', [], {'default': "''", 'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'truekko.item': {
            'Meta': {'ordering': "['-pub_date']", 'object_name': 'Item'},
            'demand': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'photo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'price': ('django.db.models.fields.IntegerField', [], {}),
            'price_type': ('django.db.models.fields.CharField', [], {'default': "'ETK'", 'max_length': '20'}),
            'pub_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'IT'", 'max_length': '2'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'items'", 'to': "orm['auth.User']"})
        },
        'truekko.itemtagged': {
            'Meta': {'object_name': 'ItemTagged'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['truekko.Item']"}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['truekko.Tag']"})
        },
        'truekko.membership': {
            'Meta': {'object_name': 'Membership'},
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['truekko.Group']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'role': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'truekko.swap': {
            'Meta': {'ordering': "['-date']", 'object_name': 'Swap'},
            'credits': ('django.db.models.fields.IntegerField', [], {}),
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'done_msg': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'user_from': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'swaps_from'", 'to': "orm['auth.User']"}),
            'user_to': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'swaps_to'", 'to': "orm['auth.User']"})
        },
        'truekko.swapcomment': {
            'Meta': {'object_name': 'SwapComment'},
            'comment': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'swap': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'comments'", 'to': "orm['truekko.Swap']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'truekko.swapitems': {
            'Meta': {'object_name': 'SwapItems'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['truekko.Item']"}),
            'swap': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'items'", 'to': "orm['truekko.Swap']"})
        },
        'truekko.tag': {
            'Meta': {'object_name': 'Tag'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'truekko.transfer': {
            'Meta': {'object_name': 'Transfer'},
            'concept': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'credits': ('django.db.models.fields.IntegerField', [], {}),
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'group_from': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'transfer_form'", 'null': 'True', 'to': "orm['truekko.Group']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user_from': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'transfer_from'", 'null': 'True', 'to': "orm['auth.User']"}),
            'user_to': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'transfer_to'", 'to': "orm['auth.User']"})
        },
        'truekko.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'credits': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'description': ('django.db.models.fields.TextField', [], {'max_length': '300', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'default': "'Unlocated'", 'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "'Unnamed'", 'max_length': '100'}),
            'photo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'rating_score': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'rating_votes': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'web': ('django.db.models.fields.URLField', [], {'default': "''", 'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'truekko.wall': {
            'Meta': {'object_name': 'Wall'},
            'description': ('django.db.models.fields.TextField', [], {'max_length': '300', 'null': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'walls'", 'null': 'True', 'to': "orm['truekko.Group']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'walls'", 'null': 'True', 'to': "orm['auth.User']"})
        },
        'truekko.wallmessage': {
            'Meta': {'ordering': "['-date']", 'object_name': 'WallMessage'},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'msg': ('django.db.models.fields.TextField', [], {}),
            'private': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'messages'", 'to': "orm['auth.User']"}),
            'wall': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'messages'", 'to': "orm['truekko.Wall']"})
        }
    }

    complete_apps = ['truekko']