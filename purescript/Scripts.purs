module Scripts (scripts, Script) where

-- Effects, types
import Prelude
import Hubot (Robot, HUBOT)
import Control.Monad.Eff (Eff)
import Node.HTTP (HTTP)
import Control.Monad.Eff.Exception (EXCEPTION)
import Control.Monad.Eff.Console (CONSOLE)

-- Scripts
import Scripts.Hoobot as Hoobot

type Script = Robot
            -> Eff ( http :: HTTP
                   , hubot :: HUBOT
                   , err :: EXCEPTION
                   , console :: CONSOLE
                   ) Unit

scripts :: Array Script
scripts = [ Hoobot.script
          ]