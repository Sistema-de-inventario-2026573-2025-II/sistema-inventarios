import logging

def test_logger_setup_import():
    """
    Prueba que el modulo de configuracion del logger existe
    y se puede importar.
    """
    try:
        from app.core.logging_setup import setup_logging
        assert setup_logging is not None
    except ImportError as e:
        # Esto es lo que esperamos
        assert False, f"Fallo la importacion del logger: {e}"

def test_logger_emits_log(caplog):
    """
    Prueba que un logger configurado emite un log.
    (Esta prueba fallara al principio, pero es nuestro objetivo)
    """
    # 'caplog' es un fixture especial de pytest
    from app.core.logging_setup import setup_logging
    
    # Configuramos el logger (asumiendo que la importacion funciona)
    setup_logging()
    
    logger = logging.getLogger("test_logger")
    
    # Emitimos un log
    logger.info("Este es un mensaje de prueba.")
    
    # Verificamos que el log fue capturado
    with caplog.at_level(logging.INFO):
        logger.info("Este es un mensaje de prueba.")
        assert "Este es un mensaje de prueba." in caplog.text