# -*- coding: utf-8 -*-
# © 2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

def convert_company_field(cr):

    cr.execute("""SELECT 1
                    FROM information_schema.columns
                   WHERE table_name = 'mis_report_instance'
                     AND column_name = 'company_id'
               """)
    if not cr.fetchone():
        return

    cr.execute("""
        UPDATE ir_model_fields
        SET name = 'company_ids',
            ttype = 'many2many',
            help = 'Select companies for which data will be searched. \
                    User's company by default.',
            relation_table = 'mis_report_instance_res_company_rel',
            column_1 = 'mis_report_instance_id',
            column_2 = 'res_company_id',
        WHERE model='mis.report.instance' AND name='company_id'
    """)

    cr.execute("""
        CREATE TABLE mis_report_instance_res_company_rel
        (
          mis_report_instance_id integer NOT NULL,
          res_company_id integer NOT NULL,
          CONSTRAINT mis_report_instance_res_company_rel_mis_report_instance_id_fkey FOREIGN KEY (mis_report_instance_id)
              REFERENCES mis_report_instance (id) MATCH SIMPLE
              ON UPDATE NO ACTION ON DELETE CASCADE,
          CONSTRAINT mis_report_instance_res_company_rel_res_company_id_fkey FOREIGN KEY (res_company_id)
              REFERENCES res_company (id) MATCH SIMPLE
              ON UPDATE NO ACTION ON DELETE CASCADE,
          CONSTRAINT mis_report_instance_res_compa_mis_report_instance_id_res_co_key UNIQUE (mis_report_instance_id, res_company_id)
        )
        WITH (
          OIDS=FALSE
        );
        ALTER TABLE mis_report_instance_res_company_rel

        COMMENT ON TABLE mis_report_instance_res_company_rel
          IS 'RELATION BETWEEN mis_report_instance AND res_company';

        CREATE INDEX mis_report_instance_res_company_rel_mis_report_instance_id_idx
          ON mis_report_instance_res_company_rel
          USING btree
          (mis_report_instance_id);

        CREATE INDEX mis_report_instance_res_company_rel_res_company_id_idx
          ON mis_report_instance_res_company_rel
          USING btree
          (res_company_id);
    """)
    
    cr.execute(
        """INSERT INTO mis_report_instance_res_company_rel
             SELECT id as mis_report_instance_id,
                    company_id as res_company_id
             FROM mis_report_instance;
        """)

def migrate(cr, version):
    cr.execute("""
        ALTER TABLE mis_report_kpi
        RENAME COLUMN expression TO old_expression
    """)
    # this migration to date_range type is partial,
    # actual date ranges needs to be created manually
    cr.execute("""
        UPDATE mis_report_instance_period
        SET type='date_range'
        WHERE type='fp'
    """)
    convert_company_field(cr)
