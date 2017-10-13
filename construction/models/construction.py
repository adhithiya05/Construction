from odoo import api, fields, models, _

# Master Data

class TaskType(models.Model):
    _name = "task.type"
    _description = "Task Type"

    name = fields.Char('Task Type Name', required = 1)
    code = fields.Char('Task Type Code')
    description = fields.Text('Description')


class TaskCategory(models.Model):
    _name = "task.category"
    _description = "Task Category"

    name = fields.Char('Task Category Name', required = 1)
    code = fields.Char('Task Category Code')
    description = fields.Text('Description')


class BOQType(models.Model):
    _name = "boq.type"
    _description = "BOQ Type"

    name = fields.Char('BOQ Type Name', size = 80, required = 1)
    code = fields.Char('BOQ Type Code', size = 80)
    description = fields.Text('Description', size = 250)


class BOQCategory(models.Model):
    _name = "boq.category"
    _description = "BOQ Category"

    name = fields.Char('BOQ Category Name', size = 80, required = 1)
    code = fields.Char('BOQ Category Code', size = 80)
    description = fields.Text('Description', size = 250)

class RelationType(models.Model):
    _name = "relation.type"
    _description = "Relation Type"

    name = fields.Char('Relation Name', size = 80, required = 1)

class WBS(models.Model):
    _name = "task.wbs"
    _description = "WBS"

    name = fields.Char('WBS  Name', size = 80, required = 1)
    code = fields.Char('WBS Code', size = 80)
    description = fields.Text('Description', size = 250)
    is_parent = fields.Boolean('Is Parent')

class MileStone(models.Model):
    _name = "task.milestone"
    _description = "Milestone"

    name = fields.Char('Milestone Name', size = 80, required = 1)
    code = fields.Char('Milestone Code', size = 80)
    description = fields.Text('Description', size = 250)

class CostCode(models.Model):
    _name = "cost.code"
    _description = "Cost Code"

    name = fields.Char('Cost  Name', size = 80, required = 1)
    code = fields.Char('Cost Code', size = 80)
    description = fields.Text('Description', size = 250)
    

# Project Setup

class ProjectSetup(models.Model):
    _name = "project.setup"
    # _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Project Setup"
    # _rec_name = 'project'

    name = fields.Char("Project", size = 80, required = 1)
    status = fields.Selection([('P', 'Pending'), ('PL', 'Planned'), ('IP', 'Inprogress'), ('C', 'Completed'), ('CL', 'Closed')], string = "Status")
    start_date = fields.Date("Project Start Date")
    end_date = fields.Date("Project End Date")
    act_start_date = fields.Date("Actual Start Date")
    act_end_date = fields.Date("Actual End Date")
    delivery_unit_ids = fields.One2many('project.deliveryunit', 'project_id')
    user_mapping_ids = fields.One2many('project.usermapping', 'project_id')
    work_scope_ids = fields.One2many('project.setup.work.scope', 'project_setup_id')
    boq_mapping_ids = fields.One2many('project.mapboq', 'project_id') 
    doc_count = fields.Integer(compute='_compute_attached_docs_count', string="Number of documents attached")
	
	
    @api.model
    def create(self, vals):
        relation_obj = self.env['task.relationship']
        scope_obj = self.env['project.setup.work.scope']
        wbs_ids = [x.id for x in self.env['task.wbs'].search([('is_parent', '=', True)])]
        res = super(ProjectSetup, self).create(vals)
        if res.work_scope_ids:
            if wbs_ids:
                task_ids =  self.env['task'].search([('wbs_id', 'in', wbs_ids)])
                scope_parent_task_ids = [x.name.id for x in res.work_scope_ids.filtered(lambda scope: scope.name.id in task_ids.ids)]
                if scope_parent_task_ids:
                    for parent in scope_parent_task_ids:
                        relation_br = relation_obj.search([('primary_task_id', '=', parent)])
                        if relation_br:
                            for relation in relation_br:
                                dict = {
                                    'name': relation.related_task_id.id,
                                    'parent_task_id': relation.primary_task_id.id,
                                    'project_id': res.id
                                }

                                scope_obj.create(dict)
        return res


    #Function to create form in project level boq

    @api.model
    def create(self, vals):
        ids = []
        project_boq_obj = self.env['project.bill.of.quantity']
        mapboq_obj = self.env['project.mapboq']
        boq_obj = self.env['bill.of.quantity']
        res = super(ProjectSetup, self).create(vals)
        if res.boq_mapping_ids:
            for item in res.boq_mapping_ids:
                ids.append(item.id)
            mapboq_br = mapboq_obj.browse(ids)
            if mapboq_br:
                for items in mapboq_br:
                    for mapboq in items:
                        dict1 = {
                            'project': res.id,
                            'boq_id': mapboq.boq_id.id,
                            }
                        boq = boq_obj.browse(mapboq.boq_id.id)
                        if boq:
                            dict2 = {
                                'boq_shr_description': boq.boq_shr_description,
                                'boq_type_id': boq.boq_type_id.id,
                                'boq_category_id': boq.boq_category_id.id,
                                'job_id': boq.job_id,
                                'status': boq.status,
                                'boq_lng_description': boq.boq_lng_description,
                                'remarks': boq.remarks,
                                'notes': boq.notes,
                                'boq_parent': boq.boq_parent,
                                'parent_boq': boq.parent_boq,
                                'boq_class': boq.boq_class
                            }
                            dict1.update(dict2)

                            project_boq_obj.create(dict1)
        return res


    @api.multi		
    def initiate_work_order(self):		
        workorder_obj = self.env['work.order.details']		
        workscope_obj = self.env['work.scope']		
        for project in self:		
            workorder = workorder_obj.create({		
                'project_no' : project.name,		
                'status': project.status,		
                'workorder_startdate': project.start_date,		
                'workorder_enddate': project.end_date,		
                'actual_startdate': project.act_start_date,		
                'actual_enddate': project.act_end_date,		
            })		
            if project.work_scope_ids:      		
                for work in project.work_scope_ids:		
                    for workscope in work:		
                        workscope_obj.create({		
                            's_no': workscope.s_no,		
                            'task_id': workscope.name.id,		
                            'parent_task_id': workscope.parent_task_id.id,		
                            'milestone_id': workscope.milestone_id.id,		
                            'wbs_id': workscope.wbs_id.id,		
                            'planed_startdate': workscope.planed_startdate,		
                            'planed_enddate': workscope.planed_enddate,		
                            'actual_startdate': workscope.actual_startdate,		
                            'actual_enddate': workscope.actual_enddate,		
                            'task_desc': workscope.task_desc,		
                            'status': workscope.status,		
                            'effort': workscope.effort,		
                            'remarks': workscope.remarks,		
                            'wo_task_type': workscope.wo_task_type,		
                            'task_class': workscope.task_class,		
                            'work_scope_id': workorder.id, 		
                        })


    def _compute_attached_docs_count(self):
        attachment = self.env['ir.attachment']
        for project in self:
            project.doc_count = attachment.search_count([
                ('res_model', '=', 'project.setup'), ('res_id', '=', project.id)
            ])


    @api.multi
    def attachment_tree_view(self):
        self.ensure_one()
        domain = [('res_model', '=', 'project.setup'), ('res_id', 'in', self.ids)]
        return {
            'name': _('Attachments'),
            'domain': domain,
            'res_model': 'ir.attachment',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'kanban,tree,form',
            'view_type': 'form',
            'help': _('''<p class="oe_view_nocontent_create">
                        Documents are attached to the project form.
                    </p>'''),
            'limit': 80,
            'context': "{'default_res_model': '%s','default_res_id': %d}" % (self._name, self.id)
        }



# Project BOQ

class ProjectBillOfQuantity(models.Model):
    _name = "project.bill.of.quantity"
    # _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Project BOQ"
    _rec_name = 'boq_id'


    project = fields.Many2one('project.setup', 'Project')
    revision = fields.Char("Revision", size = 80)
    boq_id = fields.Many2one('bill.of.quantity', string = "BOQ ID", required = 1)
    boq_shr_description = fields.Char("Description", size = 80)
    boq_type_id = fields.Many2one('boq.type', string = "BOQ Type", required = 1)
    boq_category_id = fields.Many2one('boq.category', string = "BOQ Category", required = 1)
    job_id = fields.Char("Job ID", size = 80)
    status = fields.Selection([('P', 'Pending'), ('PL', 'Planned'), ('IP', 'Inprogress'), ('C', 'Completed'), ('CL', 'Closed')], string = "Status")
    boq_lng_description = fields.Html('BOQ Long Description')
    remarks = fields.Text("Remarks", size = 250)
    notes = fields.Text("Notes", size = 250)
    boq_parent = fields.Boolean("BOQ Parent")
    parent_boq = fields.Char("Parent BOQ", size = 80)
    boq_class = fields.Selection([('group','Group'), ('detail','Detail')], default = "detail", string = "BOQ Class")    
    material_ids = fields.One2many('project.boq.details', 'project_boq_id')
    item_ids = fields.One2many('project.boq.items', 'project_boq_id')

    @api.onchange('boq_id')
    def boq_id_get(self):
        if self.boq_id:
            self.boq_type_id = self.boq_id.boq_type_id and self.boq_id.boq_type_id.id or False
            self.job_id = self.boq_id.job_id  or False
            self.notes = self.boq_id.notes  or False
            self.remarks = self.boq_id.remarks  or False
            self.boq_shr_description = self.boq_id.boq_shr_description  or False
            self.boq_category_id = self.boq_id.boq_category_id  or False
            self.status = self.boq_id.status  or False
            self.boq_parent = self.boq_id.boq_parent  or False
            self.parent_boq = self.boq_id.parent_boq  or False
            self.boq_class = self.boq_id.boq_class  or False
            self.boq_lng_description = self.boq_id.boq_lng_description or False

   
    # Function to save data in Many2one fields

    @api.model
    def create(self, vals):
        boq_items_obj = self.env['boq.items']
        boq_materials_obj = self.env['boq.details']
        pro_items_obj = self.env['project.boq.items']
        pro_materials_obj = self.env['project.boq.details']
        res = super(ProjectBillOfQuantity, self).create(vals)
        if res.boq_id:
            for items in res.boq_id.item_ids:
                for item in items:
                    boqitem = boq_items_obj.search([('id','=',item.id)])
                    if boqitem:
                        pro_items_obj.create({
                            'seq_no': boqitem.seq_no,
                            'project_boq_id': res.id,
                            'code': boqitem.code,
                            'description': boqitem.description,
                            'unit_id': boqitem.unit_id.id,
                            'quantity': boqitem.quantity,
                            'rate': boqitem.rate
                            })

            for items in res.boq_id.material_ids:
                for item in items:
                    boqmaterial = boq_materials_obj.search([('id','=',item.id)])
                    if boqmaterial:
                        pro_materials_obj.create({
                            'name': boqmaterial.name,
                            'project_boq_id': res.id,
                            'description': boqmaterial.description,
                            'uom_id': boqmaterial.uom_id.id,
                            'quantity': boqmaterial.quantity,
                            'cost_per_unit': boqmaterial.cost_per_unit 
                            })
        return res


    @api.multi
    def generate_duplicate_form(self):
        plboq_obj = self.env['project.bill.of.quantity']
        plboq_items_obj = self.env['project.boq.items']
        plboq_detail_obj = self.env['project.boq.details']
        for project in self:
            plboq = plboq_obj.create({
                'boq_id': project.boq_id.id,
                'revision': project.revision,
                'project': project.project.id,
                'boq_shr_description': project.boq_shr_description,
                'boq_type_id': project.boq_type_id.id,
                'boq_category_id': project.boq_category_id.id,
                'job_id': project.job_id,
                'status': project.status,
                'notes': project.notes,
                'remarks': project.remarks,
                'boq_parent': project.boq_parent,
                'parent_boq': project.parent_boq,
                'boq_lng_description':project.boq_lng_description
                })

            if project.item_ids:
                for items in project.item_ids:
                    for item in items:
                        plboq_items_obj.create({
                            'seq_no': item.seq_no,
                            'code': item.code,
                            'description': item.description,
                            'unit_id': item.unit_id.id,
                            'quantity': item.quantity,
                            'rate': item.rate,
                            'amount': item.amount,
                            'project_boq_id':plboq.id,

                            })

            if project.material_ids:
                for details in project.material_ids:
                    for detail in details:
                        plboq_detail_obj.create({
                            'name': detail.name,
                            'uom_id': detail.uom_id.id,
                            'description': detail.description,
                            'quantity': detail.quantity,
                            'cost_per_unit': detail.cost_per_unit,
                            'total_cost': detail.total_cost,
                            'project_boq_id':plboq.id,

                            })

            # loan.write({'state': 'move_to_approver'})
        return True
    

    # project_boq_type_id = 

    # @api.onchange('boq_id')
    # def bill_of_quan_get(self):
    #     if self.boq_id:
    #         self.boq_category_id = self.boq_id.parent_id and self.boq_id.parent_id.id or False





class Delivery(models.Model):
    _name = "project.deliveryunit"
    _description = "Delivery Unit"

    name = fields.Char("Unit ID", size = 80, required = 1)
    project_id = fields.Many2one('project.setup')
    s_no = fields.Integer('S.No', size = 80)
    description = fields.Char("Unit Description", size = 80)
    specification = fields.Char("Unit Specification", size = 80)
    customer_id = fields.Many2one('res.partner', string = "Customer")
    Contract = fields.Char("Contract", size = 80)
    remarks = fields.Text("Remarks", size = 250)


class ProjectUserMapping(models.Model):
    _name = "project.usermapping"
    _description = "Project User Mapping"

    name = fields.Many2one('res.users', string="User Name", size = 80, required = 1)
    project_id = fields.Many2one('project.setup')
    s_no = fields.Integer('S.No', size = 80)
    emp_code = fields.Char("Employee code", size = 80)
    user_type = fields.Selection([('E','Employee'), ('C', 'Customer'), ('C', 'Consultant'), ('V', 'Vendor')], string = "User Type")
    assigned_from = fields.Date("Assigned from")
    assigned_to = fields.Date("Assigned to")
    role = fields.Char("Role", size = 80)

# Task relationship

class Relationship(models.Model):
    _name = "task.relationship"
    _description = "Task Relationship"
    _rec_name = 'primary_task_id'


    def get_parent_ids(self):
        wbs_ids = [x.id for x in self.env['task.wbs'].search([('is_parent', '=', True)])]
        if wbs_ids:
            task_ids =  self.env['task'].search([('wbs_id', 'in', wbs_ids)])
            return task_ids.ids


    # name = fields.Char('Primary Task', size = 150, required = "1")
    primary_task_id = fields.Many2one('task', string = "Primary Task", required = 1)
    related_task_id = fields.Many2one('task', string = "Related Task", required = 1)
    seq_no = fields.Integer(string = "Sequence No", size = 80)
    relation_type_id = fields.Many2one('relation.type', string = "Relation Type", required = 1)
    schedule_type = fields.Selection([('SS ', 'start - start '), ('SF', 'Start - Finish'), ('FS', 'Finish - Start'), ('FF', 'Finish - Finish')], string = "Schedule Type")
    lag = fields.Float('Lag (Hours)', size = 80)
    parent_fun_ids = fields.Many2many('task', default=get_parent_ids)
    


# Task Templete

class Task(models.Model):
    _name = "task"
    _description = "Task"

    name = fields.Char('Task', size = 80, required = 1)
    task_desc = fields.Char('Task Description', size = 250)
    status = fields.Selection([('P', 'Pending'), ('PL', 'Planned'), ('IP', 'Inprogress'), ('C', 'Completed'), ('CL', 'Closed')], string = "Status")
    wbs_id = fields.Many2one('task.wbs', string = "WBS", required = 1)
    task_type_id = fields.Many2one('task.type', string = "Task Type", required = 1)
    task_category_id = fields.Many2one('task.category', string = "Task Category", required = 1)
    effort_day = fields.Float('Effort in Days', size = 80, required = True)
    elapsed_time = fields.Float('Elapsed Time', size = 80)
    remarks = fields.Text('Remarks', size = 250)
    checklist_ids = fields.One2many('project.task.checklist', 'task_id', string = "Check List")


class TaskChecklist(models.Model):
    _name = "project.task.checklist"
    _description = "Project Task Checklist"

    check_list = fields.Char('Check List', size = 150, required = 1)
    name = fields.Char('Description', size = 250)
    task_id = fields.Many2one('task')
    verification = fields.Selection([('Y', 'Yes'), ('N', 'No')], string = "Verification")
    remarks = fields.Text('Remarks', size = 250)

# Project Plan

class ProjectPlan(models.Model):
    _name = "project.plan"
    # _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Project Plan"
    _rec_name = 'project'

    project = fields.Char("Project", size = 80, required = 1)
    status = fields.Selection([('P', 'Pending'), ('PL', 'Planned'), ('IP', 'Inprogress'), ('C', 'Completed'), ('CL', 'Closed')], string = "Status")
    start_date = fields.Date("Project Start Date")
    end_date = fields.Date("Project End Date")
    act_start_date = fields.Date("Actual Start Date")
    act_end_date = fields.Date("Actual End Date")
    # work_scope = fields.One2many('project.workscope','slno')
    user_mapping_ids = fields.One2many('project.mapboq', 'project_plan_id')
    sales_order_ids = fields.One2many('project.salesorder', 'project_plan_id')
    work_order_ids = fields.One2many('project.workorder', 'project_plan_id')



class ProjectSetupWorkScope(models.Model):
    _name = "project.setup.work.scope"
    _description = " Project Work Scope Details"

    name = fields.Many2one('task', string = "Task", required=1)
    project_setup_id = fields.Many2one('project.setup')
    parent_task_id = fields.Many2one('task', string ="Parent Task")
    s_no = fields.Integer('S.No', size = 80)
    project_id = fields.Many2one('project.setup', 'Project')
    planed_startdate = fields.Date('Pln Start Date')
    planed_enddate = fields.Date('Pln End Date')
    actual_startdate = fields.Date('Act Start Date')
    actual_enddate = fields.Date('Act End Date')
    status = fields.Selection([('P', 'Pending'), ('PL', 'Planned'), ('IP', 'Inprogress'), ('C', 'Completed'), ('CL', 'Closed')], string = "Status")
    wo_task_type = fields.Selection([('T', 'Task'),('N', 'New'),('D', 'Defect')], string = "Action Type")		
    task_class = fields.Selection([('P', 'Planned'),('U', 'Unplanned')], string = "Task Class")  
    task_desc = fields.Char('Task Description', size = 120)
    wbs_id = fields.Many2one('task.wbs', string = "WBS")
    milestone_id = fields.Many2one('task.milestone', string = "Milestone")
    effort = fields.Integer('Effort in Days', size = 80)
    remarks = fields.Text('Remarks', size = 250)

    @api.onchange('name')
    def get_parent_id(self):
        relation_obj = self.env['task.relationship']
        if self.name:
            relation_br = relation_obj.search([('related_task_id', '=', self.name.id)])
            if relation_br:
                self.parent_task_id = relation_br[0].primary_task_id.id


class MapBoq(models.Model):
    _name = "project.mapboq"
    _description = "Project Map BOQ"
    _rec_name = 'boq_id'

    slno = fields.Integer("S.No", size = 80)
    project_id = fields.Many2one('project.setup')
    project_plan_id = fields.Many2one('project.plan')
    boq_id = fields.Many2one('bill.of.quantity', string = "BOQ", required = 1)
    vendor_id = fields.Many2one('res.partner', domain = [('supplier', '=', 'TRUE')], string = "Vendor", required = 1)
    vendor_contract = fields.Char("Vendor Contract", size = 80)
    remarks = fields.Text("Remarks", size = 250)
    delivery_unit = fields.Float("Delivery unit", size = 80)


class SalesOrder(models.Model):
    _name = "project.salesorder"
    _description = "Project Sales Order"
    _rec_name = 'customer'

    customer = fields.Char("Customer", size = 80)
    project_plan_id = fields.Many2one('project.plan')
    salesorder = fields.Char("Sales order", size = 80)
    total_amount = fields.Float("Total amount", size = 80)
    collected_amount = fields.Float("Collected amount", size = 80)
    pending_amount = fields.Float("Pending amount", size = 80)
    remarks = fields.Text("Remarks", size = 250)

class WorkOrder(models.Model):
    _name = "project.workorder"
    _description = "Project Work Order"
    _rec_name = 'work_orderno'

    work_orderno = fields.Integer("Work Order No", size = 80)
    project_plan_id = fields.Many2one('project.plan')
    start_date = fields.Date("Start Date")
    end_date = fields.Date("End Date")
    status = fields.Selection([('P', 'Pending'), ('PL', 'Planned'), ('IP', 'Inprogress'), ('C', 'Completed'), ('CL', 'Closed')], string = "Status")
    remarks = fields.Text("Remarks", size = 150)

# work order

class WorkOrderDetails(models.Model):
    _name = "work.order.details"
    _description = "Work Order Details"

    name = fields.Char('Work Order No', required = 0, readonly=1, track_visibility = 1)
    project_no = fields.Char('Project No', size = 120)
    workorder_startdate = fields.Date('WO Start Date')
    workorder_enddate = fields.Date('WO End Date')
    status = fields.Selection([('P', 'Pending'), ('PL', 'Planned'), ('IP', 'Inprogress'), ('C', 'Completed'), ('CL', 'Closed')], string = "Status")
    contractor = fields.Char('Contractor', size = 120)
    actual_startdate = fields.Date('Actual Start Date')
    actual_enddate = fields.Date('Actual End Date')
    wo_task_class = fields.Selection([('P', 'Planned'), ('U', 'Unplanned')], string = "WO Task Class")
    work_scope_ids = fields.One2many('work.scope', 'work_scope_id', string = "WorkScope")


    @api.model		
    def create(self, vals):		
        vals['name'] = self.env['ir.sequence'].next_by_code('work.order.details')		
        result = super(WorkOrderDetails, self).create(vals)		
        return result

class WorkScope(models.Model):
    _name = "work.scope"
    _description = "Work Scope Details"
    _rec_name = "task_id"

    # name = fields.Char('Task', size=120, required=1)
    task_id = fields.Many2one('task', string = "Task", required = 1)
    work_scope_id = fields.Many2one('work.order.details')
    s_no = fields.Integer('S.No', size = 80)
    planed_startdate = fields.Date('Pln Start Date')
    planed_enddate = fields.Date('Pln End Date')
    actual_startdate = fields.Date('Act Start Date')
    actual_enddate = fields.Date('Act End Date')
    status = fields.Selection([('P', 'Pending'),('PL', 'Planned'),('IP', 'Inprogress'),('C', 'Completed'), ('CL', 'Closed')], string = "Status")
    wo_task_type = fields.Selection([('T', 'Task'),('N', 'New'),('D', 'Defect')], string = "Action Type")
    task_desc = fields.Char('Task Description', size = 120)
    wbs_id = fields.Many2one('task.wbs', string = "WBS", required = 1)
    parent_task_id = fields.Many2one('task', string = "Parent Task", required = 1)
    # parent_task = fields.Char("Parent Task", size =150)
    milestone_id = fields.Many2one('task.milestone', string = "Milestone", required = 1)
    task_class = fields.Selection([('P', 'Planned'),('U', 'Unplanned')], string = "Task Class")
    effort = fields.Integer('Effort in Days', size = 80)
    remarks = fields.Text('Remarks', size = 150)

    @api.onchange('task_id')
    def get_parent_id(self):
        relation_obj = self.env['task.relationship']
        if self.task_id:
            relation_br = relation_obj.search([('related_task_id', '=', self.task_id.id)])
            if relation_br:
                self.parent_task_id = relation_br[0].primary_task_id.id


# BOQ

class BillOfQuantity(models.Model):
    _name = "bill.of.quantity"
    # _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Task Setup"
    _rec_name = 'boq_id'

    project = fields.Char("Project", Size = 80)
    boq_id = fields.Char("BOQ ID", size = 80, required = 1)
    boq_shr_description = fields.Char("Description", size = 80)
    boq_type_id = fields.Many2one('boq.type', string = "BOQ Type", required = 1)
    boq_category_id = fields.Many2one('boq.category', string = "BOQ Category", size = 80, required = 1)
    job_id = fields.Char("Job ID", size = 80)
    status = fields.Selection([('P', 'Pending'), ('PL', 'Planned'), ('IP', 'Inprogress'), ('C', 'Completed'), ('CL', 'Closed')], string = "Status")
    boq_lng_description = fields.Html('BOQ Long Description')
    remarks = fields.Text("Remarks", Size = 250)
    notes = fields.Text("Notes", Size = 250)
    boq_parent = fields.Boolean("BOQ Parent")
    parent_boq = fields.Char("Parent BOQ", size = 80)
    boq_class = fields.Selection([('group','Group'),('detail','Detail')], default = "detail", string = "BOQ Class")    
    material_ids = fields.One2many('boq.details', 'boq_id')
    item_ids = fields.One2many('boq.items', 'boq_id')


    @api.multi
    def generate_PLBOQ_form(self):
        plboq_obj = self.env['project.bill.of.quantity']
        for project in self:
            plboq_obj.create({
                'boq_id': project.id,
                'status': project.status,
                'start_date': project.start_date,
                'end_date': project.end_date,
                'act_start_date': project.act_start_date,
                'act_end_date': project.act_end_date,
                # 'delivery_unit_ids': project.delivery_unit_ids.ids
                # 'approver_id': loan.employee_manager_id.id
                })
            # loan.write({'state': 'move_to_approver'})
        return True


class Material(models.Model):
    _name = "boq.details"
    _description = "BOQ Details"

    name = fields.Char("Material", Size = 80)
    boq_id = fields.Many2one('bill.of.quantity')
    description = fields.Char("Description", Size = 80)
    uom_id = fields.Many2one('product.uom', string = "UOM", required = 1)
    quantity = fields.Float("Quantity", Size = 80)
    cost_per_unit = fields.Float("Cost per unit", Size = 80)

    @api.one
    @api.depends('quantity','cost_per_unit')
    def totalcost(self):
        total = self.quantity * self.cost_per_unit
        self.total_cost = total

    total_cost = fields.Float("Total Cost", store = True, compute = 'totalcost')


class BoqItems(models.Model):
    _name = "boq.items"
    _description = "BOQ Items"
    _rec_name = 'seq_no'

    seq_no = fields.Integer("S.No", Size = 80)
    boq_id = fields.Many2one('bill.of.quantity')
    code = fields.Char("Code", size = 50)
    description = fields.Text(String = "Description",Size = 250)
    unit_id = fields.Many2one('product.uom', string = "UOM", required = 1)
    quantity = fields.Float("Quantity", Size = 80)
    rate = fields.Float("Rate", Size = 80)

    @api.one
    @api.depends('quantity','rate')
    def totalcost(self):
        total = self.quantity * self.rate
        self.amount = total

    amount = fields.Float("Amount", store = True, compute = 'totalcost')


# BOQ



class ProjectMaterial(models.Model):
    _name = "project.boq.details"
    _description = "Project BOQ Details"

    name = fields.Char("Material", size = 80)
    project_boq_id = fields.Many2one('project.bill.of.quantity')
    description = fields.Char("Description", size = 80)
    uom_id = fields.Many2one('product.uom', string = "UOM", required = 1)
    quantity = fields.Float("Quantity", size = 80)
    cost_per_unit = fields.Float("Cost per unit", size = 80)

    @api.one
    @api.depends('quantity','cost_per_unit')
    def totalcost(self):
        total = self.quantity * self.cost_per_unit
        self.total_cost = total

    total_cost = fields.Float("Total Cost", store = True, compute = 'totalcost')


class ProjectBoqItems(models.Model):
    _name = "project.boq.items"
    _description = "Project BOQ Items"
    _rec_name = 'seq_no'

    seq_no = fields.Integer("S.No", size = 80)
    project_boq_id = fields.Many2one('project.bill.of.quantity')
    code = fields.Char("Code", size = 50)
    description = fields.Text(String = "Description", size = 250)
    unit_id = fields.Many2one('product.uom', string = "UOM", required = 1)
    quantity = fields.Float("Quantity", size = 80)
    rate = fields.Float("Rate", size = 80)

    @api.one
    @api.depends('quantity', 'rate')
    def totalcost(self):
        total = self.quantity * self.rate
        self.amount = total

    amount = fields.Float("Amount", store = True, compute = 'totalcost')


# Project BOQ

# Time sheet

class TimeSheet(models.Model):
    _name = "work.order.timesheet"
    _description = "Work Order Timesheet"
    _rec_name = 'work_order_id'

    recording_date = fields.Date("Recording Date")
    work_order_id = fields.Many2one('work.order.details', string = "Work Order", required = 1)
    task_id = fields.Many2one('work.scope', string = "WO Task", required = 1)
    emp_code_id = fields.Many2one('hr.employee', string = "Employee code", required = 1)
    startdate = fields.Date('Start Date')
    enddate = fields.Date('End Date')
    effort = fields.Integer('Effort in Days', size = 80)
    complete = fields.Boolean('Complete')
    remarks = fields.Text('Remarks', size = 250)


# CRM change order

class ChangeOrder(models.Model):
    _name = "crm.change.order"
    _description = "CRM Chenge Order"

    name = fields.Char('Change Order', size = 120, required = 1)
    customer = fields.Char('Customer', size = 120)
    date = fields.Date('Date')
    status = fields.Selection([('A','Active'), ('I', 'Inactive')], string = "Status")
    change_order_type = fields.Char('Change Order Type', size = 120)
    change_order_category = fields.Char('Change Order Category', size = 120)
    raised_by = fields.Selection([('C','Customer'), ('I', 'Internal')], string = "Raised by")
    cost_paid_by = fields.Selection([('C','Customer'), ('I', 'Internal')], string = "Cost Paid by")
    change_order_details = fields.Char('Change Order Details', size = 120)
    change_order_boq = fields.Char('Change Order BOQ', size = 120)
    boq_impact_details = fields.Char('BOQ Impact Details', size = 120)
    cost = fields.Float('Cost', size = 80)
    remarks = fields.Text('Remarks', size = 150)
    
# CRM Manage leads

class CrmProcessLead(models.Model):
    _name = "crm.process.lead"
    _description = "CRM Process"
    _rec_name = "lead_ref_id"

    lead_ref_id = fields.Char("Lead Ref ID", size = 50)
    lead_details = fields.Char("Lead Details", size = 50)
    responsibility = fields.Char("Responsibility", size = 50)
    contact_interest = fields.Char("Contact Interest", size = 50)
    property_interested = fields.Char("Property Interested", size = 50)
    budget = fields.Char("Budget", size = 50)
    floor = fields.Char("Floor", size = 50)
    date = fields.Date("Date")
    lead_source = fields.Char("Lead Source", size = 50)
    lead_status = fields.Selection([('meeting','Meeting Scheduled'),('negotiation','Negotiation'),('agreement','Agreement Signed'),('registration','Registration Completed')], string = "Lead Status")
    other_comments = fields.Char("Comments", size = 50)
    house_preference = fields.Char("House Preference", size = 50)
    facing = fields.Selection([('east','East'), ('west','West'), ('north','North'), ('south','South')], string = "Facing")

    # Contact details
    customer_id_ref = fields.Char("Lead Ref ID", size = 50)
    first_name = fields.Char("First Name", size = 50)
    last_name = fields.Char("Last Name", size = 50)
    address_1 = fields.Text("Address")
    address_2 = fields.Text("Address")
    company_name = fields.Char("Company Name", size = 50)
    mobile_no_1 = fields.Char("Mobile No 1")
    mobile_no_2 = fields.Char("Mobile No 2")
    landline_no = fields.Char("Landline No")
    email_id_1 = fields.Char("Email ID 1", size = 50)
    email_id_2 = fields.Char("Email ID 2", size = 50)
    skype_id = fields.Char("Skype ID", size = 50)
    twitter = fields.Char("Twitter", size = 50)
    facebook = fields.Char("Facebook", size = 50)
    other_social_media = fields.Char("Other Social Media", size = 50)
    company_URL = fields.Char("Company URL", size = 50)

    # Payment Preference
    payment_type = fields.Selection([('BL','Bank Loan'),('RC','Ready Cash'),('B','Both')], string = "Payment Type")
    loan_amount = fields.Char("Loan Amount", size = 50)
    remarks = fields.Char("Remarks", size = 50)
    preferred_bank = fields.Char("Preferred Bank", size = 50)
    direct_cash = fields.Char("Direct Cash", size = 50)
    other_prefer = fields.Char("Other Preference", size = 50)

    team_ids = fields.One2many('crm.lead.team','crm_lead_id')
    activity_ids = fields.One2many('crm.lead.activity', 'crm_lead_id')


class CrmLeadTeam(models.Model):
    _name = "crm.lead.team"
    _description = "CRM Lead Team"
    _rec_name = "user"

    user = fields.Char("User", size = 50)
    crm_lead_id = fields.Char('crm.process.lead')
    employee_code = fields.Char("Employee Code", size = 50)
    employee_name = fields.Char("Employee Name", size = 50)
    start_date = fields.Char("Start Date", size = 50)
    end_date = fields.Char("End Date", size = 50)


class CrmLeadActivity(models.Model):
    _name = "crm.lead.activity"
    _description = "CRM Lead Activity"
    _rec_name = "task"

    task = fields.Char("Task", size = 50)
    crm_lead_id = fields.Char('crm.process.lead')
    target_date = fields.Char("Target Date", size = 50)
    priority = fields.Selection([('L','Low'),('M','Medium'),('H','High'),('C','Critical')], string = "Priority")
    status = fields.Selection([('P','Planned'),('C','Completed'),('CL','Closed')], string = "Status")
    assigned_to_id = fields.Many2one('hr.employee', string = "Assigned To")
    remarks = fields.Char("Remarks", size = 50)
    
# Manage sale order

class CrmProcessSaleorder(models.Model):
    _name = "crm.process.saleorder"
    _description = "CRM Process Saleorder"

    name = fields.Char("Sale Order", size = 80, required = 1)
    sale_order_date = fields.Date("Sale Order Date")
    customer = fields.Char("Customer", size = 80)
    pay_term = fields.Char("Pay Term", size = 0)
    responsibility = fields.Char("Responsibility", size = 80)
    status = fields.Char("Status", size = 80)
    details = fields.Char("Details", size = 80)
    contract = fields.Char("Contract", size = 80)
    customization_req = fields.Selection([('A','Allowed'),('N','Not Allowed')], string = "Customization")
    customization_boq = fields.Char("Customization BOQ")
    lead_ref_id = fields.Char("Lead Ref ID", size = 50)
    project_details_ids = fields.One2many('crm.sale.project','crm_sale_id')
    payment_schedule_ids = fields.One2many('crm.sale.payment','crm_sale_id')


class CrmSaleProjectDetails(models.Model):
    _name = "crm.sale.project"
    _description = "CRM Sale Project Details"

    name = fields.Char("Project", size = 80, required = 1)
    crm_sale_id = fields.Many2one('crm.process.saleorder')
    project_unit = fields.Char("Project Unit", size = 80)
    floor = fields.Char("Floor", size = 80)
    spec = fields.Char("Specification", size = 80)
    uds = fields.Integer("UDS", size = 80)
    carpet_area = fields.Integer("Carpet Area", size = 80)
    buildup_area = fields.Integer("Buildup Area", size = 80)
    comments = fields.Char("Comments", size = 80)


class CrmSalePaymentSchedule(models.Model):
    _name = "crm.sale.payment"
    _description = "CRM Sale Project Payment"

    name = fields.Char("Sechedule No", size = 80, required = 1)
    crm_sale_id = fields.Many2one('crm.process.saleorder')
    pay_element = fields.Char("Pay Element", size = 80)
    schedule_date = fields.Date("Schedule Date")
    amount =  fields.Float("Amount", size = 80)
    pay_mode = fields.Char("Pay Mode", size = 80)
    billed_amount = fields.Float("Billed Amount", size = 80)
    paid_amount = fields.Float("Paid Amount", size = 80)
    bank_details = fields.Char("Bank Details", size = 80)
    remarks = fields.Char("Remarks", size = 250)


 # Issue Tracking

class IssueTracking(models.Model):
    _name = "crm.issue.tracking"
    _description = "CRM Issue Tracking"
    _rec_name = "issue_no"

    issue_no = fields.Integer("Issue No", size = 80)
    date = fields.Date("Date")
    issue_type = fields.Char("Issue Type", size = 80)
    description = fields.Text("Description", size = 250)
    priority = fields.Selection([('L','Low'),('M','Medium'),('H','High'),('C','Critical')], string = "Priority")
    other_info = fields.Text("Description", size = 80)
    customer = fields.Char("Customer", size = 80)
    issue_category = fields.Char("Issue Category", size = 80)
    status = fields.Selection([('P','Pending'),('A','Assigned'),('C','Completed')], string = "Status")



# Material Consumption

class MaterialConsumption(models.Model):
    _name = "material.consumption"
    _description = "Material Consumption"
   

    name = fields.Char("Material", size = 80, required = 1)
    recording_date = fields.Date("Recording Date")
    project_id = fields.Many2one('project.setup', string = "Project")
    work_order_id = fields.Many2one('work.order.details', string = "Work Order")
    task_id = fields.Many2one('task', string = "Task")
    uom_id = fields.Many2one('product.uom', string = "UOM")
    unit_cost = fields.Float("Unit Cost", size = 80)
    total_cost = fields.Float("Total Cost", size = 80)
    cost_code = fields.Char("Cost Code", size = 80)


# Budget

class Budget(models.Model):
    _name = "budget"
    _description = "Budget"
   

    project_id = fields.Many2one('project.setup', string = "Project")
    cost_code = fields.Char("Cost Code", size = 80)
    budget_amount = fields.Float("Budget Amount", size = 80)
    consumed_amount = fields.Float("Consumed Amount", size = 80)
    positive_tolerance = fields.Float("Positive Tolerance", size = 80)
    negative_tolerance = fields.Float("Negative Tolerance", size = 80)
    remarks = fields.Text("Remarks", size = 250)
    
