from playwright.sync_api import sync_playwright

def bloquear_redirecciones_eficazmente():
    with sync_playwright() as p:
        # Inicia el navegador
        browser = p.chromium.launch(headless=False)  # Modo visible para observar el comportamiento
        context = browser.new_context()

        # Abre una nueva página
        page = context.new_page()

        # Intercepta solicitudes y bloquea redirecciones
        def handle_route(route, request):
            # Bloquear cualquier solicitud a páginas de mantenimiento o redirección
            if "mantenimiento" in request.url or "redir" in request.url:
                print(f"Intento de redirección bloqueado: {request.url}")
                route.abort()
            else:
                route.continue_()

        # Interceptar todas las solicitudes
        page.route("**/*", handle_route)

        # Maneja eventos de navegación y evita redirecciones indeseadas
        def on_navigation(route):
            # Si la navegación no es a la URL principal, la bloqueamos
            if route.request.url != 'https://www.vtv.minfra.gba.gob.ar/historial.php':
                print(f"Redirección detectada y bloqueada a: {route.request.url}")
                route.abort()
            else:
                route.continue_()

        # Bloqueo de navegaciones no deseadas
        page.on("framenavigated", lambda frame: frame.stop())

        # Navega a la página de inicio y evita redirecciones inmediatas
        try:
            page.goto('https://www.vtv.minfra.gba.gob.ar/historial.php', wait_until='domcontentloaded')

            # Ejecuta scripts preventivos para deshabilitar redirecciones en el DOM
            page.evaluate('''
                // Detener cualquier acción de navegación inmediatamente
                window.stop();

                // Deshabilitar redirecciones mediante window.location
                Object.defineProperty(window, 'location', {
                    configurable: false,
                    enumerable: true,
                    value: window.location,
                    writable: false
                });

                // Anular métodos de redirección
                ['assign', 'replace', 'reload'].forEach(fn => {
                    window.location[fn] = function() { console.log(`Intento de redirección bloqueado: ${fn}`); };
                });

                // Bloquea redirección mediante window.location.href
                Object.defineProperty(window.location, 'href', {
                    set: function() {
                        console.log('Intento de redirección a través de window.location.href bloqueado.');
                    }
                });

                // Eliminar meta refresh tags
                const metas = document.querySelectorAll('meta[http-equiv="refresh"]');
                metas.forEach(meta => meta.parentNode.removeChild(meta));
            ''')
        except Exception as e:
            print(f"Error durante la carga y bloqueo: {e}")

        # Interactúa con la página para verificar que está operativa sin redirección
        try:
            # Rellenar el campo de patente y realizar acciones necesarias
            page.fill('#patente', 'AA123BB')
        except Exception as e:
            print(f"Error durante la interacción con la página: {e}")

        # Mantener la página abierta para verificación manual
        print("Verifica la página y presiona Enter para cerrar...")
        input()

        # Cierra el navegador
        browser.close()

# Ejecutar la función para bloquear redirecciones
bloquear_redirecciones_eficazmente()
