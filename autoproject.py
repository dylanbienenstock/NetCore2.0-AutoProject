#!/usr/bin/python

import sys, os, string
from string import Template
from os.path import *

name = raw_input("Project name: ")
db_name = raw_input("Database name: ")
ctrl_name = raw_input("Controller name: ")

def path_to(str):
	return normpath(join(os.getcwd(), str))

print("\nCreating project " + name + "\n")

os.mkdir(path_to(name))
os.chdir(path_to(name))

os.system("dotnet new web")
os.system("dotnet add package Microsoft.Extensions.Configuration.Json")
os.system("dotnet add package Npgsql.EntityFrameworkCore.PostgreSQL")
os.system("dotnet add package Microsoft.EntityFrameworkCore.Tools")
os.system("dotnet add package Microsoft.EntityFrameworkCore.Tools.DotNet")
os.system("dotnet add package Microsoft.AspNetCore.Identity.EntityFrameworkCore")

print("\nCreating directory Models/")
os.mkdir(path_to("Models"))

print("Creating directory Views/")
os.mkdir(path_to("Views"))

print("Creating directory Views/Shared/")
os.mkdir(path_to("Views/Shared"))

print("Creating directory Views/" + ctrl_name + "/")
os.mkdir(path_to("Views/" + ctrl_name))

print("Creating directory Controllers/")
os.mkdir(path_to("Controllers"))

print("Creating directory wwwroot/css/")
os.mkdir(path_to("wwwroot/css"))

print("\nDownloading normalize.css")
normalize_css = "https://raw.githubusercontent.com/necolas/normalize.css/master/normalize.css"
os.system("wget -O " + path_to("wwwroot/css/normalize.css") + " " + normalize_css)

###### <name>.csproj ###########################################################

print("Altering " + name + ".csproj\n")
name_csproj = open(path_to(name + ".csproj"), "w")
name_csproj.write("""<Project Sdk="Microsoft.NET.Sdk.Web">

	<PropertyGroup>
		<TargetFramework>netcoreapp2.0</TargetFramework>
	</PropertyGroup>

	<ItemGroup>
		<Folder Include="wwwroot\" />
	</ItemGroup>

	<ItemGroup>
		<PackageReference Include="Microsoft.AspNetCore.All" Version="2.0.0" />
		<PackageReference Include="Microsoft.EntityFrameworkCore.Tools" Version="2.0.0" />
		<PackageReference Include="Microsoft.EntityFrameworkCore.Tools.DotNet" Version="2.0.0" />
		<PackageReference Include="Microsoft.Extensions.Configuration.Json" Version="2.0.0" />
		<PackageReference Include="Npgsql.EntityFrameworkCore.PostgreSQL" Version="2.0.0" />
		<PackageReference Include="Microsoft.AspNetCore.Identity.EntityFrameworkCore" Version="2.0.0" />
	</ItemGroup>

	<ItemGroup>
		<DotNetCliToolReference Include="Microsoft.EntityFrameworkCore.Tools.DotNet" Version="2.0.0" />
	</ItemGroup> 

</Project>""")
name_csproj.close()

###### appsettings.json ########################################################

print("Writing appsettings.json")
appsettings_json = open(path_to("appsettings.json"), "w")
appsettings_json.write(Template("""{
	"DBInfo":
	{
		"Name": "PostGresConnect",
		"ConnectionString": "server=localhost;userId=postgres;password=postgres;port=5432;database=${db_name};"
	}
}""").substitute(db_name=db_name))
appsettings_json.close()

###### <ctrl_name>Controller.cs ################################################

print("Writing " + ctrl_name + "Controller.cs")
controller_cs = open(path_to("Controllers/" + ctrl_name + "Controller.cs"), "w")
controller_cs.write(Template("""using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;

namespace ${name}
{
	public class ${ctrl_name}Controller : Controller
	{
		[HttpGet]
		[Route("")]
		public IActionResult Index()
		{
			return View();
		}
	}
}""").substitute(name=name, ctrl_name=ctrl_name))
controller_cs.close()

###### DatabaseOptions.cs ######################################################

print("Writing DatabaseOptions.cs")
DatabaseOptions_cs = open(path_to("DatabaseOptions.cs"), "w")
DatabaseOptions_cs.write(Template("""namespace ${name}
{
	public class DatabaseOptions
	{
		public string Name { get; set; }
		public string ConnectionString { get; set; }
	}
}""").substitute(name=name))
DatabaseOptions_cs.close()

###### DatabaseContext.cs ######################################################

print("Writing Models/DatabaseContext.cs")
DatabaseContext_cs = open(path_to("Models/DatabaseContext.cs"), "w")
DatabaseContext_cs.write(Template("""using Microsoft.EntityFrameworkCore;

namespace ${name}.Models
{
	public class DatabaseContext : DbContext
	{
		public DatabaseContext(DbContextOptions<DatabaseContext> options) : base(options) { }
	}
}""").substitute(name=name))
DatabaseContext_cs.close()

###### BaseModel.cs ############################################################

print("Writing Models/BaseModel.cs")
BaseModel_cs = open(path_to("Models/BaseModel.cs"), "w")
BaseModel_cs.write(Template("""using System;

namespace ${name}.Models
{
	public abstract class BaseModel
	{
		public int Id { get; set; }
		public DateTime CreatedAt { get; set; }
		public DateTime UpdatedAt { get; set; }
	}
}""").substitute(name=name))
BaseModel_cs.close()

###### BaseViewModel.cs ########################################################

print("Writing Models/BaseViewModel.cs")
BaseViewModel_cs = open(path_to("Models/BaseViewModel.cs"), "w")
BaseViewModel_cs.write(Template("""namespace ${name}.Models
{
	public abstract class BaseViewModel { }
}""").substitute(name=name))
BaseViewModel_cs.close()

###### User.cs ########################################################

print("Writing Models/User.cs")
BaseViewModel_cs = open(path_to("Models/User.cs"), "w")
BaseViewModel_cs.write(Template("""using Microsoft.AspNetCore.Identity;

namespace ${name}.Models
{
	public class User : IdentityUser { }
}""").substitute(name=name))
BaseViewModel_cs.close()

###### Startup.cs ##############################################################

print("Writing Startup.cs")
Startup_cs = open(path_to("Startup.cs"), "w")
Startup_cs.write(Template("""using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Configuration;
using Microsoft.EntityFrameworkCore;
using Microsoft.AspNetCore.Identity;
using Microsoft.AspNetCore.Identity.EntityFrameworkCore;

using ${name}.Models;

namespace ${name}
{
	public class Startup
	{
		public IConfiguration Configuration { get; private set; }

		public Startup(IHostingEnvironment env)
		{
			var builder = new ConfigurationBuilder()
			.SetBasePath(env.ContentRootPath)
			.AddJsonFile("appsettings.json", optional: true, reloadOnChange: true)
			.AddEnvironmentVariables();
			Configuration = builder.Build();
		}

		public void ConfigureServices(IServiceCollection services)
		{
			services.AddDbContext<DatabaseContext>(options => options.UseNpgsql(Configuration["DBInfo:ConnectionString"]));

			services.AddIdentity<User, IdentityRole>()
			.AddEntityFrameworkStores<DatabaseContext>()
			.AddDefaultTokenProviders();

			services.Configure<IdentityOptions>(options =>
			{
				options.Password.RequireDigit = false;
				options.Password.RequiredLength = 8;
				options.Password.RequireNonAlphanumeric = false;
				options.Password.RequireUppercase = false;
				options.Password.RequireLowercase = false;
				options.Password.RequiredUniqueChars = 6;

				options.Lockout.DefaultLockoutTimeSpan = TimeSpan.FromMinutes(30);
				options.Lockout.MaxFailedAccessAttempts = 10;
				options.Lockout.AllowedForNewUsers = true;

				options.User.RequireUniqueEmail = true;
			});

			services.ConfigureApplicationCookie(options =>
			{
				options.Cookie.HttpOnly = true;
				options.Cookie.Expiration = TimeSpan.FromDays(150);
				options.LoginPath = "/Account/Login";
				options.LogoutPath = "/Account/Logout";
				options.AccessDeniedPath = "/Account/AccessDenied";
				options.SlidingExpiration = true;
			});

			services.AddSession();
			services.AddMvc();
		}

		public void Configure(IApplicationBuilder app, IHostingEnvironment env)
		{
			if (env.IsDevelopment())
			{
				app.UseDeveloperExceptionPage();
			}

			app.UseStaticFiles();
			app.UseSession();
			app.UseMvc();
		}
	}
}""").substitute(name=name))
Startup_cs.close()

###### styles.css ##############################################################

print("Writing wwwroot/css/styles.css")
styles_css = open(path_to("wwwroot/css/styles.css"), "w")
styles_css.write(Template("""html, body {
	margin: 0;
	padding: 0;
}

h1, h2, h3, h4, p {
	margin-top: 0;
}""").substitute(name=name))
styles_css.close()

###### _ViewStart.cshtml #######################################################

print("Writing Views/_ViewStart.cshtml")
_ViewStart_cshtml = open(path_to("Views/_ViewStart.cshtml"), "w")
_ViewStart_cshtml.write(Template("""@{
	Layout = "~/Views/Shared/Layout.cshtml";
}""").substitute(name=name))
_ViewStart_cshtml.close()

###### _ViewImports.cs #########################################################

print("Writing Views/_ViewImports.cshtml")
_ViewImports_cshtml = open(path_to("Views/_ViewImports.cshtml"), "w")
_ViewImports_cshtml.write(Template("""@using ${name}
@using ${name}.Models
@addTagHelper *, Microsoft.AspNetCore.Mvc.TagHelpers""").substitute(name=name))
_ViewImports_cshtml.close()

###### Layout.cshtml ###########################################################

print("Writing Views/Shared/Layout.cshtml")
Layout_cshtml = open(path_to("Views/Shared/Layout.cshtml"), "w")
Layout_cshtml.write(Template("""<!DOCTYPE html>

<html>
	<head>
		<link rel="stylesheet" href="~/css/normalize.css">
		<link rel="stylesheet" href="~/css/styles.css">

		<title>@ViewBag.Title - ${name}</title>
	</head>

	<body>
		@RenderBody()
	</body>
<html>""").substitute(name=name))
Layout_cshtml.close()

###### Index.cshtml ############################################################

print("Writing Views/" + ctrl_name + "/Index.cshtml")
Index_cshtml = open(path_to("Views/" + ctrl_name + "/Index.cshtml"), "w")
Index_cshtml.write(Template("""@{
	ViewBag.Title = "Hello world!";
}

<h1>Hello world!</h1>""").substitute(name=name))
Index_cshtml.close()

###### FINALIZE ################################################################

print("\nc: c: c: c: c: c: c: c: c: c: c: c: c: c: c: c: c: c: c: c:\n")

os.system("dotnet clean")
os.system("dotnet restore")

###### GIT #####################################################################

print("Writing .gitignore")
gitignore = open(path_to(".gitignore"), "w")
gitignore.write("appsettings.json")
gitignore.close()

print("Writing README.md")
README_md = open(path_to("README.md"), "w")
README_md.write(Template("""# ${name}
A brand new .NET Core 2.0 project generated using Dylan's script!""").substitute(name=name))
README_md.close()

os.system("git init")
os.system("git add --all")
os.system("git commit -m \"Initial commit\"")

print("\nDone <3\n")