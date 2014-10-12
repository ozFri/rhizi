import unittest
import db_controller
import logging
import db_controller as dbc

from rhizi_server import Config

class TestDBController(unittest.TestCase):

    db_ctl = None
    log = None

    n_map = { 'Skill': [{'name': 'Kung Fu', 'id': 'skill_00' },
                        {'name': 'Judo', 'id': 'skill_01' }
                        ],

              'Person': [{'name': 'Bob', 'id': 'person_00', 'age': 128 },
                         {'name': 'Alice', 'id': 'person_01', 'age': 256 }
                         ]
            }

    @classmethod
    def setUpClass(self):
        cfg = Config.init_from_file('res/etc/rhizi-server.conf')
        self.db_ctl = dbc.DB_Controller(cfg)
        self.db_ctl.exec_op(dbc.DBO_add_node_set(self.n_map))
        self.log = logging.getLogger('rhizi')

    def setUp(self):
        pass

    def test_db_op_statement_iteration(self):
        s_arr = ['create (b:Book {title: \'foo\'}) return b',
                 'match (n) return n',]

        op = dbc.DB_op()
        op.add_statement(s_arr[0])
        op.add_statement(s_arr[1])

        i = 0
        for s_id, s, r in op:
            # access: second tuple item -> REST-form 'statement' key
            self.assertEqual(s_arr[i], s['statement'])
            self.assertEqual(None, r)
            i = i + 1
            
        self.db_ctl.exec_op(op)

        i = 0
        for s_id, s, r in op:
            # access: second tuple item -> REST-form 'statement' key
            self.assertNotEqual(None, r)
            i = i + 1

    def test_add_link_set(self):
        l_map = { 'Knows' : [{'__src': 'person_00', '__dst': 'skill_00'},
                             {'__src': 'person_00', '__dst': 'skill_01'}] }
        l_set = self.db_ctl.exec_op(dbc.DBO_add_link_set(l_map))
        self.assertEqual(len(l_set), 2)
    
    def test_load_node_set_by_type(self):
        filter_type = 'Person'
        n_set = self.db_ctl.exec_op(dbc.DBO_load_node_id_set(filter_type=filter_type))
        self.assertEqual(len(n_set), 2)

        filter_type = 'Nan_Type'
        n_set = self.db_ctl.exec_op(dbc.DBO_load_node_id_set(filter_type=filter_type))
        self.assertEqual(len(n_set), 0)

    def test_load_node_set_by_attribute(self):
        filter_map = { 'name': ['Bob', u'Judo'],
                       'age': [128] }
        n_set = self.db_ctl.exec_op(dbc.DBO_load_node_set_by_attribute(filter_map))
        self.assertEqual(len(n_set), 1)

        filter_map = { 'age': [128, 256, 404] }
        n_set = self.db_ctl.exec_op(dbc.DBO_load_node_set_by_attribute(filter_map))
        self.assertEqual(len(n_set), 2)

    def test_load_node_set_by_id_attribute(self):
        n_set = self.db_ctl.exec_op(dbc.DBO_load_node_set_by_id_attribute(['skill_00', 'person_01']))
        self.assertEqual(len(n_set), 2)

    def test_load_link_set_by_src_or_dst_id_attributes(self):
        op = dbc.DBO_load_link_set_by_src_or_dst_id_attributes(src_id='person_00', dst_id='skill_00')
        n_set = self.db_ctl.exec_op(op)
        self.assertEqual(len(n_set), 1)
        
        op = dbc.DBO_load_link_set_by_src_or_dst_id_attributes(src_id='person_00')
        n_set = self.db_ctl.exec_op(op)
        self.assertEqual(len(n_set), 2)

        op = dbc.DBO_load_link_set_by_src_or_dst_id_attributes(dst_id='skill_00')
        n_set = self.db_ctl.exec_op(op)
        self.assertEqual(len(n_set), 1)

    def test_node_DB_id_lifecycle(self):
        """
        test node DB id life cycle
        """
        id_set = self.db_ctl.exec_op(dbc.DBO_add_node_set({'Person': [{'name': 'John Doe', 'id': 'jdoe_00'},
                                                                      {'name': 'John Doe', 'id': 'jdoe_01'}]}))
        n_set = self.db_ctl.exec_op(dbc.DBO_load_node_set_by_DB_id(id_set))
        self.assertEqual(len(n_set), len(id_set), 'incorrect result size')

    def test_load_node_set_by_DB_id(self): pass # TODO

    def test_partial_query_set_execution_success(self):
        """
        test:
            - statement execution stops at first invalid statement
            - assert create statement with result data does not actually persist in DB 
            
        From the REST API doc: 'If any errors occur while executing statements,
        the server will roll back the transaction.'
        """
        n_id = 'test_partial_query_set_execution_success'
        
        op = dbc.DB_op()
        op.add_statement("create (n:Person {id: '%s'}) return n" % (n_id), {}) # valid statement
        op.add_statement("match (n) return n", {}) # valid statement
        op.add_statement("non-valid statement #1", {})
        op.add_statement("non-valid statement #2", {})
        
        self.db_ctl.exec_op(op)
        
        self.assertEqual(len(op.result_set), 2)
        self.assertEqual(len(op.error_set), 1)

        # assert node creation did not persist
        n_set = self.db_ctl.exec_op(dbc.DBO_load_node_set_by_id_attribute([n_id]))
        self.assertEqual(len(n_set), 0)

    def tearDown(self): pass

if __name__ == "__main__":
    unittest.main()
