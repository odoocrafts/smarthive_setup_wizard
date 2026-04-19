from odoo import models, fields, api, _
from odoo.exceptions import UserError

class SmarthiveSetupWizard(models.TransientModel):
    _name = 'smarthive.setup.wizard'
    _description = 'Smarthive Setup Wizard'

    state = fields.Selection([
        ('welcome', 'Welcome'),
        ('company', 'Company Setup'),
        ('sales_team', 'Sales Team Setup'),
        ('salesperson', 'Salesperson Setup'),
        ('courses', 'Courses Setup'),
        ('intro_books', 'Books App Intro'),
        ('intro_student', 'Student Management Intro'),
        ('help', 'Help & Support'),
        ('done', 'Done')
    ], string='Status', default='welcome')

    # Company Fields
    company_name = fields.Char(string="Company Name")
    company_logo = fields.Image(string="Company Logo")
    street = fields.Char()
    street2 = fields.Char()
    city = fields.Char()
    state_id = fields.Many2one('res.country.state', string="State")
    zip = fields.Char()
    country_id = fields.Many2one('res.country', string="Country")
    phone = fields.Char()
    email = fields.Char()

    # Sales Team Fields
    sales_team_name = fields.Char(string="Sales Team Name", default="Main Sales Team")

    # Lines
    salesperson_line_ids = fields.One2many('smarthive.setup.salesperson.line', 'wizard_id', string="Salespeople")
    course_line_ids = fields.One2many('smarthive.setup.course.line', 'wizard_id', string="Courses")

    @api.model
    def default_get(self, fields_list):
        res = super(SmarthiveSetupWizard, self).default_get(fields_list)
        company = self.env.company
        res.update({
            'company_name': company.name,
            'company_logo': company.logo,
            'street': company.street,
            'street2': company.street2,
            'city': company.city,
            'state_id': company.state_id.id if company.state_id else False,
            'zip': company.zip,
            'country_id': company.country_id.id if company.country_id else False,
            'phone': company.phone,
            'email': company.email,
        })
        return res

    def action_next(self):
        states = ['welcome', 'company', 'sales_team', 'salesperson', 'courses', 'intro_books', 'intro_student', 'help', 'done']
        current_index = states.index(self.state)
        
        if current_index < len(states) - 1:
            self.state = states[current_index + 1]
            
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'smarthive.setup.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def action_previous(self):
        states = ['welcome', 'company', 'sales_team', 'salesperson', 'courses', 'intro_books', 'intro_student', 'help', 'done']
        current_index = states.index(self.state)
        
        if current_index > 0:
            self.state = states[current_index - 1]
            
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'smarthive.setup.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def action_finish(self):
        # Update Company
        company = self.env.company
        company.write({
            'name': self.company_name or company.name,
            'logo': self.company_logo or company.logo,
            'street': self.street,
            'street2': self.street2,
            'city': self.city,
            'state_id': self.state_id.id if self.state_id else False,
            'zip': self.zip,
            'country_id': self.country_id.id if self.country_id else False,
            'phone': self.phone,
            'email': self.email,
        })

        # Create Sales Team
        team = False
        if self.sales_team_name:
            team = self.env['crm.team'].create({
                'name': self.sales_team_name,
                'use_leads': True,
                'use_opportunities': True,
            })

        # Create Salespeople
        for sp in self.salesperson_line_ids:
            if not sp.name or not sp.login:
                continue
            
            groups_val = []
            sale_group = self.env.ref('sales_team.group_sale_salesman', raise_if_not_found=False)
            if sale_group:
                groups_val.append((4, sale_group.id))
            
            user_group = self.env.ref('base.group_user', raise_if_not_found=False)
            if user_group:
                groups_val.append((4, user_group.id))

            user_vals = {
                'name': sp.name,
                'login': sp.login,
                'password': sp.password,
                'groups_id': groups_val
            }
            if team:
                user_vals['sale_team_id'] = team.id

            self.env['res.users'].create(user_vals)

        # Create Courses
        for course in self.course_line_ids:
            if not course.name:
                continue
            self.env['product.product'].create({
                'name': course.name,
                'course_code': course.course_code,
                'course_type': course.course_type,
                'semester_count': course.semester_count,
                'is_it_required_university': False,
                'type': 'service',
            })

        # Hide the setup menu item since it is completely finished
        setup_menu = self.env.ref('smarthive_setup_wizard.menu_smarthive_setup_root', raise_if_not_found=False)
        if setup_menu:
            setup_menu.active = False

        return {'type': 'ir.actions.act_window_close'}


class SmarthiveSetupSalespersonLine(models.TransientModel):
    _name = 'smarthive.setup.salesperson.line'
    _description = 'Setup Salesperson Line'

    wizard_id = fields.Many2one('smarthive.setup.wizard')
    name = fields.Char(string="Name", required=True)
    login = fields.Char(string="Email / Login", required=True)
    password = fields.Char(string="Password", required=True)


class SmarthiveSetupCourseLine(models.TransientModel):
    _name = 'smarthive.setup.course.line'
    _description = 'Setup Course Line'

    wizard_id = fields.Many2one('smarthive.setup.wizard')
    name = fields.Char(string="Course Name", required=True)
    course_code = fields.Char(string="Course Code")
    course_type = fields.Selection([
        ("degree", "Degree"),
        ("diploma", "Diploma"),
        ("certificate", "Certificate"),
    ], string="Course Type")
    semester_count = fields.Integer(string="Semester Count", default=1)
