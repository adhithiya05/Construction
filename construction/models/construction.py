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

class Milestone(models.Model):
    _name = "task.milestone"
    _description = "Milestone"

    name = fields.Char('Milestone Name', size = 80, required = 1)
    code = fields.Char('Milestone Code', size = 80)
    description = fields.Text('Description', size = 250)

   


# Project Setup

class ProjectSetup(models.Model):
    _name = "project.setup"
    # _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Project Setup"
    _rec_name = 'project'

    project = fields.Char("Project", size = 80, required = 1)
    status = fields.Selection([('P', 'Pending'), ('PL', 'Planned'), ('IP', 'Inprogress'), ('C', 'Completed'), ('CL', 'Closed')], string = "Status")
    start_date = fields.Date("Project Start Date")
    end_date = fields.Date("Project End Date")
    act_start_date = fields.Date("Actual Start Date")
    act_end_date = fields.Date("Actual End Date")
    delivery_unit_ids = fields.One2many('project.deliveryunit', 'project_deliveryunit')
    user_mapping_ids = fields.One2many('project.usermapping', 'project_usermapping')
    work_scope_ids = fields.One2many('project.setup.work.scope', 'project_setup_work_scope')
    boq_mapping_ids = fields.One2many('project.mapboq', 'project_mapboq') 

    def _compute_attached_docs_count(self):
        Attachment = self.env['ir.attachment']
        for project in self:
            project.doc_count = Attachment.search_count([
                '|',
                '&',
                ('res_model', '=', 'project.project'), ('res_id', '=', project.id),
                '&',
                ('res_model', '=', 'project.task'), ('res_id', 'in', project.task_ids.ids)
            ])


    @api.multi
    def attachment_task_tree_view(self):
        self.ensure_one()
        domain = [
            '|',
            '&', ('res_model', '=', 'project.project'), ('res_id', 'in', self.ids),
            '&', ('res_model', '=', 'project.task'), ('res_id', 'in', self.task_ids.ids)]
        return {
            'name': _('Attachments'),
            'domain': domain,
            'res_model': 'ir.attachment',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'kanban,tree,form',
            'view_type': 'form',
            'help': _('''<p class="oe_view_nocontent_create">
                        Documents are attached to the tasks and issues of your project.</p><p>
                        Send messages or log internal notes with attachments to link
                        documents to your project.
                    </p>'''),
            'limit': 80,
            'context': "{'default_res_model': '%s','default_res_id': %d}" % (self._name, self.id)
        }

   
    doc_count = fields.Integer(compute='_compute_attached_docs_count', string="Number of documents attached")
    task_ids = fields.One2many('project.task', 'project_id', string='Tasks',
                               domain=['|', ('stage_id.fold', '=', False), ('stage_id', '=', False)])
    



class delivery(models.Model):
    _name = "project.deliveryunit"
    _description = "Delivery Unit"

    name = fields.Char("Unit ID", size = 80, required = 1)
    project_deliveryunit = fields.Char()
    description = fields.Char("Unit Description", size = 80)
    specification = fields.Char("Unit Specification", size = 80)
    customer = fields.Char("Customer", size = 80)
    Contract = fields.Char("Contract", size = 80)
    remarks = fields.Text("Remarks", size = 250)


class projectusermapping(models.Model):
    _name = "project.usermapping"
    _description = "Project User Mapping"

    name = fields.Char("User Name", size = 80, required = 1)
    project_usermapping = fields.Char()
    emp_code = fields.Char("Employee code", size = 80)
    user_type = fields.Selection([('E','Employee'), ('C', 'Customer'), ('C', 'Consultant'), ('V', 'Vendor')], string = "User Type")
    assigned_from = fields.Date("Assigned from")
    assigned_to = fields.Date("Assigned to")
    role = fields.Char("Role", size = 80)

# Task relationship

class Relationship(models.Model):
    _name = "task.relationship"
    _description = "Task Relationship"
    _rec_name = 'pri_name_id'


    # name = fields.Char('Primary Task', size = 150, required = "1")
    pri_name_id = fields.Many2one('task', string = "Primary Task", required = 1)
    related_task_id = fields.Many2one('task', string = "Related Task", required = 1)
    seq_no = fields.Integer(string = "Sequence No", size = 80)
    relation_type_id = fields.Many2one('relation.type', string = "Relation Type", required = 1)
    schedule_type = fields.Selection([('SS ', 'start - start '), ('SF', 'Start - Finish'), ('FS', 'Finish - Start'), ('FF', 'Finish - Finish')], string = "Schedule Type")
    lag = fields.Float('Lag (Hours)', size = 80)
    


# Task Templete

class Task(models.Model):
    _name = "task"
    _description = "Task"

    name = fields.Char('Task', size = 80, required = 1)
    task_desc = fields.Char('Task Description', size = 250)
    status = fields.Selection([('A', 'Active'), ('I', 'Inactive')], string = "Status")
    wbs_id = fields.Many2one('task.wbs', string = "WBS", required = 1)
    task_type_id = fields.Many2one('task.type', string = "Task Type", required = 1)
    task_category_id = fields.Many2one('task.category', string = "Task Category", required = 1)
    effort_day = fields.Float('Effort', size = 80, required = True)
    elapsed_time = fields.Float('Elapsed Time', size = 80)
    remarks = fields.Text('Remarks', size = 250)
    checklist_ids = fields.One2many('project.task.checklist', 'project_task_checklist', string = "Check List")


class TaskChecklist(models.Model):
    _name = "project.task.checklist"
    _description = "Project Task Checklist"

    check_list = fields.Char('Check List', size = 150, required = 1)
    name = fields.Char('Description', size = 250)
    project_task_checklist = fields.Char()
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
    user_mapping_ids = fields.One2many('project.mapboq', 'project_plan')
    sales_order_ids = fields.One2many('project.salesorder', 'project_salesorder')
    work_order_ids = fields.One2many('project.workorder', 'project_workorder')



# class workscope(models.Model):
#     _name = "project.workscope"
#     _description = "Project Work Scope"

#     slno = fields.Integer("SL.No")
#     job_id = fields.Many2one('task.relationship', string="Job ID")
#     start_date = fields.Date("Start Date")
#     end_date = fields.Date("End Date")
#     act_start_date = fields.Date("Actual Start Date")
#     act_end_date = fields.Date("Actual End Date")
#     phase = fields.Char("Phase")
#     completion = fields.Float("% Completion")
#     remarks = fields.Text("Remarks")

class ProjectsetupWorkScope(models.Model):
    _name = "project.setup.work.scope"
    _description = " Project Work Scope Details"

    # name = fields.Char('Task', size = 120, required = 1)
    name = fields.Many2one('task', string = "Task", required=1)
    project_setup_work_scope = fields.Char()
    parent_task_id = fields.Many2one('task', string ="Parent Task", required=0)
    s_no = fields.Integer('S.No', size = 80)
    project_id = fields.Many2one('project.setup', 'Project')
    planed_startdate = fields.Date('Pln Start Date')
    planed_enddate = fields.Date('Pln End Date')
    actual_startdate = fields.Date('Act Start Date')
    actual_enddate = fields.Date('Act End Date')
    status = fields.Selection([('P', 'Pending'), ('PL', 'Planned'), ('IP', 'Inprogress'), ('C', 'Completed'), ('CL', 'Closed')], string = "Status")
    task_desc = fields.Char('Task Description', size = 120)
    wbs_id = fields.Many2one('task.wbs', string = "WBS", required = 1)
    # parent_task = fields.Char("Parent Task", size = 150)
    milestone_id = fields.Many2one('task.milestone', string = "Milestone", required = 1)
    # task_class = fields.Selection([('P', 'Planned'),('U', 'Unplanned')], string ="Task Class")
    effort = fields.Integer('Effort Hours', size = 80)
    remarks = fields.Text('Remarks', size = 250)

class mapboq(models.Model):
    _name = "project.mapboq"
    _description = "Project Map BOQ"
    _rec_name = 'boq_id'

    slno = fields.Integer("SL.No", size = 80)
    project_mapboq = fields.Char()
    project_plan = fields.Char()
    boq_id = fields.Many2one('bill.of.quantity', string = "BOQ", required = 1)
    vendor_id = fields.Many2one('res.partner', domain = [('supplier', '=', 'TRUE')], string = "Vendor", required = 1)
    vendor_contract = fields.Char("Vendor Contract", size = 80)
    remarks = fields.Text("Remarks", size = 250)
    delivery_unit = fields.Float("Delivery unit", size = 80)


class salesorder(models.Model):
    _name = "project.salesorder"
    _description = "Project Sales Order"
    _rec_name = 'customer'

    customer = fields.Char("Customer", size = 80)
    project_salesorder = fields.Char()
    salesorder = fields.Char("Sales order", size = 80)
    total_amount = fields.Float("Total amount", size = 80)
    collected_amount = fields.Float("Collected amount", size = 80)
    pending_amount = fields.Float("Pending amount", size = 80)
    remarks = fields.Text("Remarks", size = 250)

class workorder(models.Model):
    _name = "project.workorder"
    _description = "Project Work Order"
    _rec_name = 'work_orderno'

    work_orderno = fields.Integer("Work Order No", size = 80)
    project_workorder = fields.Char()
    start_date = fields.Date("Start Date")
    end_date = fields.Date("End Date")
    status = fields.Selection([('A','Active'), ('I', 'Inactive')], string = "Status")
    remarks = fields.Text("Remarks", size = 150)

# work order

class WorkOrderDetails(models.Model):
    _name = "work.order.details"
    _description = "Work Order Details"

    name = fields.Char('Work Order No', size = 120, required = 1)
    project_no = fields.Char('Project No', size = 120)
    workorder_startdate = fields.Date('WO Start Date')
    workorder_enddate = fields.Date('WO End Date')
    status = fields.Selection([('P', 'Pending'), ('PL', 'Planned'), ('IP', 'Inprogress'), ('C', 'Completed'), ('CL', 'Closed')], string = "Status")
    contractor = fields.Char('Contractor', size = 120)
    actual_startdate = fields.Date('Actual Start Date')
    actual_enddate = fields.Date('Actual End Date')
    wo_task_class = fields.Selection([('P', 'Planned'), ('U', 'Unplanned')], string = "WO Task Class")
    work_scope_ids = fields.One2many('work.scope', 'work_scope', string = "WorkScope")


class WorkScope(models.Model):
    _name = "work.scope"
    _description = "Work Scope Details"
    _rec_name = "task_id"

    # name = fields.Char('Task', size=120, required=1)
    task_id = fields.Many2one('task', string = "Task", required = 1)
    work_scope = fields.Char()
    s_no = fields.Integer('S.No', size = 80)
    planed_startdate = fields.Date('Pln Start Date')
    planed_enddate = fields.Date('Pln End Date')
    actual_startdate = fields.Date('Act Start Date')
    actual_enddate = fields.Date('Act End Date')
    status = fields.Selection([('P', 'Pending'),('PL', 'Planned'),('IP', 'Inprogress'),('C', 'Completed'), ('CL', 'Closed')], string = "Status")
    wo_task_type = fields.Selection([('N', 'New'),('E', 'Existing'),('D', 'Defect')], string = "WO Task Type")
    task_desc = fields.Char('Task Description', size = 120)
    wbs_id = fields.Many2one('task.wbs', string = "WBS", required = 1)
    parent_map_task_id = fields.Many2one('task', domain = [('name','=','group')], string = "Task", required = 1)
    # parent_task = fields.Char("Parent Task", size =150)
    milestone_id = fields.Many2one('task.milestone', string = "Milestone", required = 1)
    task_class = fields.Selection([('P', 'Planned'),('U', 'Unplanned')], string = "Task Class")
    effort = fields.Integer('Effort Hours', size = 80)
    remarks = fields.Text('Remarks', size = 150)


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
    status = fields.Selection([('A','Active'), ('I', 'Inactive')], default = "A", string = "Status")
    boq_lng_description = fields.Html('BOQ Long Description')
    remarks = fields.Text("Remarks", Size = 250)
    notes = fields.Text("Notes", Size = 250)
    boq_parent = fields.Boolean("BOQ Parent")
    parent_boq = fields.Char("Parent BOQ", size = 80)
    boq_class = fields.Selection([('group','Group'),('detail','Detail')], default = "detail", string = "BOQ Class")    
    material_ids = fields.One2many('boq.details', 'boq_detail')
    item_ids = fields.One2many('boq.items', 'boq_item')


class Material(models.Model):
    _name = "boq.details"
    _description = "BOQ Details"

    name = fields.Char("Material", Size = 80)
    boq_detail = fields.Char()
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
    boq_item = fields.Char()
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

# Project BOQ

class ProjectBillOfQuantity(models.Model):
    _name = "project.bill.of.quantity"
    # _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Project BOQ"
    _rec_name = 'boq_id'

    name = fields.Char("Project", size = 80, required = 1)
    revision = fields.Char("Revision", size = 80)
    boq_id = fields.Many2one('bill.of.quantity', string = "BOQ ID", required = 1)
    boq_shr_description = fields.Char("Description", size = 80)
    boq_type_id = fields.Many2one('boq.type', string = "BOQ Type", required = 1)
    boq_category_id = fields.Many2one('boq.category', string = "BOQ Category", required = 1)
    job_id = fields.Char("Job ID", size = 80)
    status = fields.Selection([('A','Active'), ('I', 'Inactive')], default = "A", string = "Status")
    boq_lng_description = fields.Html('BOQ Long Description')
    remarks = fields.Text("Remarks", size = 250)
    notes = fields.Text("Notes", size = 250)
    boq_parent = fields.Boolean("BOQ Parent")
    parent_boq = fields.Char("Parent BOQ", size = 80)
    boq_class = fields.Selection([('group','Group'), ('detail','Detail')], default = "detail", string = "BOQ Class")    
    material_ids = fields.One2many('project.boq.details', 'project_boq_details')
    item_ids = fields.One2many('project.boq.items', 'project_boq_items')
    # project_boq_type_id = 

    # @api.onchange('boq_id')
    # def bill_of_quan_get(self):
    #     if self.boq_id:
    #         self.boq_category_id = self.boq_id.parent_id and self.boq_id.parent_id.id or False


class ProjectMaterial(models.Model):
    _name = "project.boq.details"
    _description = "Project BOQ Details"

    name = fields.Char("Material", size = 80)
    project_boq_details = fields.Char()
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
    project_boq_items = fields.Char()
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

class Timesheet(models.Model):
    _name = "work.order.timesheet"
    _description = "Work Order Timesheet"
    _rec_name = 'work_order_id'

    recording_date = fields.Date("Recording Date")
    work_order_id = fields.Many2one('work.order.details', string = "Work Order", required = 1)
    task_id = fields.Many2one('work.scope', string = "WO Task", required = 1)
    emp_code_id = fields.Many2one('hr.employee', string = "Employee code", required = 1)
    startdate = fields.Date('Start Date')
    enddate = fields.Date('End Date')
    effort = fields.Integer('Effort', size = 80)
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

    team_ids = fields.One2many('crm.lead.team','crm_lead_team')
    activity_ids = fields.One2many('crm.lead.activity', 'crm_lead_activity')


class CrmLeadTeam(models.Model):
    _name = "crm.lead.team"
    _description = "CRM Lead Team"
    _rec_name = "user"

    user = fields.Char("User", size = 50)
    crm_lead_team = fields.Char()
    employee_code = fields.Char("Employee Code", size = 50)
    employee_name = fields.Char("Employee Name", size = 50)
    start_date = fields.Char("Start Date", size = 50)
    end_date = fields.Char("End Date", size = 50)


class CrmLeadActivity(models.Model):
    _name = "crm.lead.activity"
    _description = "CRM Lead Activity"
    _rec_name = "task"

    task = fields.Char("Task", size = 50)
    crm_lead_activity = fields.Char()
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
    project_details_ids = fields.One2many('crm.sale.project','crm_sale_project')
    payment_schedule_ids = fields.One2many('crm.sale.payment','crm_sale_payment')


class CrmSaleProjectdetails(models.Model):
    _name = "crm.sale.project"
    _description = "CRM Sale Project Details"

    name = fields.Char("Project", size = 80, required = 1)
    crm_sale_project = fields.Char()
    project_unit = fields.Char("Project Unit", size = 80)
    floor = fields.Char("Floor", size = 80)
    spec = fields.Char("Specification", size = 80)
    uds = fields.Integer("UDS", size = 80)
    carpet_area = fields.Integer("Carpet Area", size = 80)
    buildup_area = fields.Integer("Buildup Area", size = 80)
    # parking = fields.Selection([('Y','Yes'),('N','No')], string="Parking")
    # park_spec = fields.Char("Parking Specification")
    comments = fields.Char("Comments", size = 80)


class CrmSalePaymentSchedule(models.Model):
    _name = "crm.sale.payment"
    _description = "CRM Sale Project Payment"

    name = fields.Char("Sechedule No", size = 80, required = 1)
    crm_sale_payment = fields.Char()
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
