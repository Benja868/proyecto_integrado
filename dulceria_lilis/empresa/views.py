from django.shortcuts import render

def informacion_empresa(request):
    context = {
        'historia': """
            Lilis Gourmet nació en 2017 como un emprendimiento familiar liderado por Liliana, 
            quien, tras dejar su trabajo en la industria acuícola, decidió iniciar un negocio 
            de producción de galletas artesanales. A partir de una producción doméstica, 
            lograron escalar a una planta propia de más de 450 m², alcanzando distribución 
            nacional a través de Unimarc, Jumbo, Santa Isabel y Aeropuertos. En 2020 comenzaron 
            exportaciones a EE. UU. bajo el programa Pyme Global.
        """,
        'mision': """
            Continuar haciendo lo que amamos a lo largo de nuestra historia, seguir innovando 
            y desarrollando mágicas recetas con sus presentaciones y mantener siempre esta 
            estrecha relación que hoy nos mueve con nuestros clientes y empleados. No solo 
            queremos crecer, también queremos aportar a nuestra sociedad con ayuda social, 
            cuidar nuestro medio ambiente, crear fuentes de trabajo para las mujeres de nuestro 
            País y con llevar todo ese cariño y compromiso que nos hace ser quien hoy día somos.
        """,
        'vision': """
            Consolidarnos como una empresa líder en la producción de dulces artesanales, 
            reconocida por nuestra calidad, innovación y compromiso social, expandiendo 
            nuestra presencia tanto a nivel nacional como internacional.
        """,
        'valores': [
            "Respeto",
            "Puntualidad", 
            "Honestidad",
            "Honradez",
            "Innovación",
            "Calidad",
            "Compromiso social"
        ],
        'contactos': {
            'Dirección': 'Avenida Amanecer #2030, Local Boci@Lilia FT-8, Centro Empresarial Coquimbo',
            'Teléfono': '+56 51 234 5678',
            'Email': 'ventas@lilis.cl',
            'Sitio web': 'www.lilis.cl'
        },
        'redes_sociales': {
            'Instagram': 'https://instagram.com/dulceria_lilis',
            'Facebook': 'https://facebook.com/lilisdulces'
        }
    }
    return render(request, 'empresa/informacion_empresa.html', context)